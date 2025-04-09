import os
import datetime
import traceback
import time

# 获取脚本启动时间（统一时间戳）
SCRIPT_START_TIME = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 设置要忽略的路径（可以是文件或目录），支持相对路径（如 ./path 或 ../path）
IGNORE_PATHS = [
    # 示例忽略路径，请根据实际需要修改
    # "path/to/ignore_directory",
    # "path/to/specific_file.ipynb"
    "./12_test_metal_lom_qubits_cpw/0.ipynb",
    "./5_test_equ_circ/demo.ipynb"
]

def should_ignore(path, ignore_list):
    """
    检查给定路径是否在忽略列表中
    
    参数:
        path: 要检查的路径
        ignore_list: 忽略路径列表
        
    返回:
        bool: 如果路径应该被忽略则返回True
    """
    abs_path = os.path.abspath(path)
    for ignore_path in ignore_list:
        # 处理相对路径（包括./和../开头的路径）
        if not os.path.isabs(ignore_path):
            # 将相对路径转换为绝对路径（基于当前工作目录）
            ignore_path = os.path.normpath(os.path.join(os.getcwd(), ignore_path))
        abs_ignore = os.path.abspath(ignore_path)
        
        # 检查是否是目录路径
        if os.path.isdir(abs_ignore):
            if abs_path.startswith(abs_ignore + os.sep) or abs_path == abs_ignore:
                return True
        # 检查是否是文件路径
        elif os.path.isfile(abs_ignore):
            if abs_path == abs_ignore:
                return True
    return False

def find_all_extension_name(extension_name):
    """
    找到本目录以及子目录下所有扩展名为 extension 的文件，返回这些文件的绝对路径。
    忽略IGNORE_PATHS中指定的路径。

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
        # 从待遍历目录中移除忽略的目录
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), IGNORE_PATHS)]
        
        for file in files:
            file_path = os.path.join(root, file)
            # 检查文件扩展名是否匹配且不在忽略列表中
            if file.endswith(extension_name) and not should_ignore(file_path, IGNORE_PATHS):
                # 将匹配的文件的绝对路径加入列表
                abso_path_list.append(file_path)

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
            start_time = time.time()  # 记录开始时间
            ep.preprocess(notebook, {'metadata': {'path': current_dir}})
            end_time = time.time()  # 记录结束时间
            elapsed_time = end_time - start_time  # 计算耗时
        return True, elapsed_time, None
    except Exception as e:
        error_info = traceback.format_exc()
        return False, 0, error_info
    
def save_error_log(error_info, notebook_path):
    # 使用脚本启动时间作为统一时间戳
    error_log_dir = os.path.join("99_error_log", SCRIPT_START_TIME)
    
    # 创建目录（如果不存在）
    os.makedirs(error_log_dir, exist_ok=True)
    
    # 获取相对于当前工作目录的路径
    relative_path = os.path.relpath(notebook_path, os.getcwd())
    
    # 创建错误日志文件路径 - 将路径分隔符替换为冒号
    safe_filename = relative_path.replace(os.sep, "：").replace(":", "")
    error_log_file = os.path.join(error_log_dir, f"{safe_filename}.txt")
    
    # 保存错误信息到文件
    with open(error_log_file, 'w', encoding='utf-8') as f:
        # 第一行明确标注文件路径
        f.write(f"Error occurred in: {os.path.abspath(notebook_path)}\n")
        f.write("="*80 + "\n")  # 分隔线
        f.write(error_info)
    
    return error_log_file

def format_time(seconds):
    """将秒数格式化为更易读的时间字符串"""
    if seconds < 60:
        return f"{seconds:.2f}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes}分{seconds:.2f}秒"
    else:
        hours = int(seconds // 3600)
        remaining_seconds = seconds % 3600
        minutes = int(remaining_seconds // 60)
        seconds = remaining_seconds % 60
        return f"{hours}小时{minutes}分{seconds:.2f}秒"

# 主程序
if __name__ == "__main__":
    # 找到所有.ipynb文件
    target_files = find_all_extension_name(".ipynb")

    # 设置环境变量避免某些警告
    os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'

    print(f"Batch execution started at: {SCRIPT_START_TIME}")
    print(f"Found {len(target_files)} notebook files to execute")
    print(f"Ignoring paths: {IGNORE_PATHS if IGNORE_PATHS else 'None'}")
    print("-" * 80)

    # 初始化统计信息
    total_files = len(target_files)
    success_count = 0
    failure_count = 0
    total_time = 0.0

    # 遍历并执行所有文件
    for notebook_file in target_files:
        print(f"Processing: {notebook_file}")
        success, elapsed_time, error_info = execute_notebook_without_interruption(notebook_file)
        if success:
            formatted_time = format_time(elapsed_time)
            print(f"[SUCCESS] {notebook_file}")
            print(f"(耗时: {formatted_time})")
            success_count += 1
            total_time += elapsed_time
        else:
            error_log_path = save_error_log(error_info, notebook_file)
            print(f"[FAILURE] {notebook_file}")
            print(f"    Error log saved to: {error_log_path}")
            failure_count += 1
        print("-" * 80)

    # 输出总结信息
    print("\nBatch execution completed")
    print(f"Total files processed: {total_files}")
    print(f"Success: {success_count}")
    print(f"Failure: {failure_count}")
    print(f"Total execution time: {format_time(total_time)}")
    if success_count > 0:
        print(f"Average time per successful notebook: {format_time(total_time/success_count)}")