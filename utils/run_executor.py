import importlib
import os
import time


from plots.test_module.draw_population import draw_PF
from utils.information_parser import convert_config_to_numeric
from utils.result_io import save_test_module_information_results
from views.common.GlobalVar import global_vars
from multiprocessing import Manager, Pipe, Process
import threading

def load_main_class_from_folder(folder_path):
    """
    给定一个文件夹路径，加载其中的 main.py 并返回其中定义的类（与文件夹同名）
    """
    main_path = os.path.join(folder_path, "main.py")
    module_name = os.path.basename(folder_path)

    if not os.path.isfile(main_path):
        raise FileNotFoundError(f"No main.py found in {folder_path}")

    spec = importlib.util.spec_from_file_location(module_name, main_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 默认类名就是文件夹名，例如 NSGA2 目录下就是 NSGA2 类
    class_name = os.path.basename(folder_path)
    if not hasattr(module, class_name):
        raise AttributeError(f"{class_name} class not found in {main_path}")

    return getattr(module, class_name)


def run_in_test_mode(response_strategy, search_algorithm, problem_name, result_to_show: str, runtime_config: dict):
    """运行测试模式：已有子进程则恢复，否则启动新进程"""
    current_process = global_vars['test_module'].get("current_process")
    current_state = global_vars['test_module'].get("process_state")

    if current_process and current_process.is_alive():
        if current_state:
            current_state.value = 'running'
        print("[主进程] 已有子进程，已发送恢复指令")
        return

    start_new_test_process(response_strategy, search_algorithm, problem_name, result_to_show, runtime_config)

def start_new_test_process(response_strategy, search_algorithm, problem_name, result_to_show: str, runtime_config: dict):
    """启动一个新的子进程并监听 Pipe"""
    manager = Manager()
    state = manager.Value('c', 'running')
    parent_conn, child_conn = Pipe()

    p = Process(
        target=run_in_test_mode_process,
        args=(response_strategy, search_algorithm, problem_name, result_to_show, runtime_config, state, child_conn),
        name="TestOptimizer"
    )

    save_state_in_test_mode(state, p, parent_conn,child_conn)
    p.start()
    threading.Thread(
        target=listen_pipe,
        args=(parent_conn, p),
        daemon=True
    ).start()



def run_in_test_mode_process(response_strategy, search_algorithm, problem_name, result_to_show: str, runtime_config,
                             state, child_conn):
    """独立子进程中执行的优化逻辑"""
    try:
        print("Subprocess started for test mode optimization...")

        # 加载类
        ResponseClass = load_main_class_from_folder(response_strategy['folder_name'])
        SearchClass = load_main_class_from_folder(search_algorithm['folder_name'])
        ProblemClass = load_main_class_from_folder(problem_name['folder_name'])

        # 实例化对象
        response_instance = ResponseClass(**convert_config_to_numeric(runtime_config['selected_dynamic']))
        search_instance = SearchClass(**convert_config_to_numeric(runtime_config['selected_search']), state=state,pip=child_conn)
        problem_instance = ProblemClass(**convert_config_to_numeric(runtime_config['selected_problem']))

        search_instance.optimize(problem_instance, response_instance)
    except Exception as e:
        print(f"[Error in subprocess]: {e}")


def save_state_in_test_mode(state, p, parent_conn,child_conn):
    global_vars['test_module']["process_state"] = state
    global_vars['test_module']["current_process"] = p
    global_vars['test_module']["parent_conn"] = parent_conn
    global_vars['test_module']["child_conn"] = child_conn
    global_vars['process_manager'][p.name] = {"process_state": state, "current_process": p, "parent_conn": parent_conn, "child_conn":child_conn}
    global_vars['test_module']["runtime_populations"] = {}


def delete_state_in_test_mode():
    if "current_process" in global_vars['test_module'] and global_vars['test_module']["current_process"] is not None:
        p = global_vars['test_module']["current_process"]
        global_vars['test_module']["child_conn"].close()  # 显式关闭 Pipe
        print("close child")
        if p.is_alive():
            p.terminate()
            print('杀死了进程')
        global_vars['process_manager'][p.name] = None
        global_vars['test_module']["process_state"] = None
        global_vars['test_module']["current_process"] = None
        global_vars['test_module']["parent_conn"] = None
        global_vars['test_module']["child_conn"] = None
        global_vars['test_module']["runtime_populations"] = {}



# 主进程监听 pipe
def listen_pipe(parent_conn, process):
    print("[主进程] Pipe监听已启动")
    try:
        while True:
            time.sleep(0.2)  # 避免空转

            # 检查子进程是否还活着
            if not process.is_alive():
                print("[主进程] 子进程已结束，Pipe监听线程退出")
                break
            # 安全地 poll Pipe
            if parent_conn.poll():
                try:
                    information = parent_conn.recv()
                    # print(f"[主进程] 收到子进程信息")
                    save_runtime_population_information(information)
                    canvas = global_vars['test_module']['canvas']
                    ax = global_vars['test_module']['ax']
                    # 更新图表
                    draw_PF(information,ax)
                    # 刷新 Canvas
                    canvas.draw()
                    # 如果执行完毕则对结果进行文件保存
                    if is_runtime_over(information):
                        save_test_module_information_results()
                except EOFError:
                    print("[主进程] Pipe连接已关闭（EOF）")
                    break
    except (BrokenPipeError, OSError) as e:
        print(f"[主进程] Pipe监听异常中止: {e}")
    finally:
        print("[主进程] close parent")
        parent_conn.close()

def is_runtime_over(information):
    change_each_evaluations = information["settings"]["problem_params"]["change_each_evaluations"]
    total_change_time = information["settings"]["problem_params"]["total_change_time"]
    max_evaluations = change_each_evaluations * total_change_time
    return information["evaluate_times"] >= max_evaluations

def save_runtime_population_information(information):
    t = information["t"]
    evaluate_times = information["evaluate_times"]

    # 确保 'runtime_populations' 字典存在
    if "runtime_populations" not in global_vars['test_module']:
        global_vars['test_module']["runtime_populations"] = {}

    # 初始化该代数 t 的信息
    if t not in global_vars['test_module']["runtime_populations"]:
        global_vars['test_module']["runtime_populations"][t] = {}

    # 保存信息
    global_vars['test_module']["runtime_populations"][t][evaluate_times] = information
