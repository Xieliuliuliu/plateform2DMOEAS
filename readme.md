# plateform2DMOEAS

📚 **简介**
------------------------------------------------------------

该框架用于实验和测试各类动态多目标算法在不同 benchmarks 和实际问题下的表现。本框架旨在提供一个结构化、可视化的实验环境，方便参数设置、问题选择、算法设计、和性能评估。

⚙️ 本框架将持续加入多种算法的实现，并可以轻松地进行扩展以加入新的算法或模块。

🔍 **注意**  
实现和结果仅供参考。如果你有更好的实现或改进建议，欢迎通过提交 **Issue** 或 **Email** 与我们进行沟通。我们鼓励社区的反馈和贡献！

## 📂 项目结构 (Project Structure)

```text
plateform2DMOEAS/
├── algorithms/ # 算法实现
│ ├── response_strategy/ # 响应策略相关算法
│ ├── search_algorithm/ # 搜索算法实现
├── components/ # 框架组件
├── plots/ # 可视化绘图模块
├── problems/ # 问题定义
│ ├── benchmark/ # 基准测试问题
│ ├── real_problem/ # 实际问题定义
├── utils/ # 工具函数
├── views/ # 用户界面相关
├── main.py # 主程序入口
```


💻 **依赖安装**
------------------------------------------------------------

在开始使用框架之前，首先需要安装相关的依赖库。以下是框架所需的所有库及其安装方式：

```bash
# 1. 克隆仓库
git clone https://github.com/Xieliuliuliu/plateform2DMOEAS.git
cd plateform2DMOEAS

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 开始运行
python main.py
```

📧 联系方式
------------------------------------------------------------
- Issues提交地址: https://github.com/Xieliuliuliu/plateform2DMOEAS/issues
- Email: xiejinsong@whu.edu.cn & 189818372@qq.com

🌟 感谢
------------------------------------------------------------
我们感谢所有的贡献者和研究人员！欢迎⭐ Star 和 🔱 Fork！

✅ 许可协议
------------------------------------------------------------
本项目采用 MIT 许可证。

🌐 后续计划
------------------------------------------------------------
目前该框架处于初步阶段，功能不完善，我们计划在未来继续实现该框架的更多功能，并搭建一个专门的网站，提供该框架的详细描述、文档、教程和使用示例。网站将帮助用户更方便地理解框架的功能与使用方法，并为社区提供一个更好的交流平台。
