import os
import datetime
import traceback

# 获取脚本启动时间（统一时间戳）
SCRIPT_START_TIME = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def find_all_extension_name(extension_name):
    """
    找到本目录以及子目录下所有扩展名为 extension 的文件，返回这些文件的绝对路径。

    输入：
        extension_name: str, 要寻找的文件扩展名，例如".ipynb", ".txt"

    输出:
        abso_path_list: list[str, str, ...], 绝对路径的集合
    """
    print("searching")

    # 检查输入的扩展名是否以 "." 开头，如果没有则自动补充
    if not extension_name.startswith("."):
        extension_name = "." + extension_name

    abso_path_list = []

    # 使用 os.walk 遍历当前目录及其子目录
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            # 检查文件扩展名是否匹配
            if file.endswith(extension_name):
                # 将匹配的文件的绝对路径加入列表
                abso_path_list.append(os.path.join(root, file))

    return abso_path_list

def execute_notebook_without_interruption(notebook_path):
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor
    import asyncio

    # Set the event loop policy to avoid warnings
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Get the current working directory
    current_dir = os.path.dirname(notebook_path)
    try:
        with open(notebook_path, 'r', encoding='utf-8') as nb_file:
            notebook = nbformat.read(nb_file, as_version=4)
            ep = ExecutePreprocessor(timeout=600, kernel_name='qeda_env')
            ep.preprocess(notebook, {'metadata': {'path': current_dir}})
        return True, None
    except Exception as e:
        error_info = traceback.format_exc()
        return False, error_info
    
def save_error_log(error_info, notebook_path):
    # 使用脚本启动时间作为统一时间戳
    error_log_dir = os.path.join("99_error_log", SCRIPT_START_TIME)
    
    # 创建目录（如果不存在）
    os.makedirs(error_log_dir, exist_ok=True)
    
    # 创建错误日志文件路径
    notebook_name = os.path.basename(notebook_path)
    error_log_file = os.path.join(error_log_dir, f"{notebook_name}.txt")
    
    # 保存错误信息到文件
    with open(error_log_file, 'w', encoding='utf-8') as f:
        # 第一行明确标注文件路径
        f.write(f"Error occurred in: {os.path.abspath(notebook_path)}\n")
        f.write("="*80 + "\n")  # 分隔线
        f.write(error_info)
    
    return error_log_file

# 主程序
if __name__ == "__main__":
    # 找到所有.ipynb文件
    target_files = find_all_extension_name(".ipynb")

    # 设置环境变量避免某些警告
    os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'

    print(f"Batch execution started at: {SCRIPT_START_TIME}")
    print(f"Found {len(target_files)} notebook files to execute")

    # 遍历并执行所有文件
    for notebook_file in target_files:
        success, error_info = execute_notebook_without_interruption(notebook_file)
        if success:
            print(f"[SUCCESS] {notebook_file}")
        else:
            error_log_path = save_error_log(error_info, notebook_file)
            print(f"[FAILURE] {notebook_file}")
            print(f"    Error log saved to: {error_log_path}")

    print("Batch execution completed")