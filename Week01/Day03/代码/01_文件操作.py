"""
Day03 - 文件操作示例
演示文件读写、路径处理等核心操作
"""

from pathlib import Path
import json


def demo_file_basic():
    """基本文件操作"""
    print("=== 基本文件操作 ===")
    
    # 写入文件
    with open('demo.txt', 'w', encoding='utf-8') as f:
        f.write('Hello, Python!\n')
        f.write('文件操作很简单\n')
        f.write('第三行内容\n')
    
    # 读取全部
    with open('demo.txt', 'r', encoding='utf-8') as f:
        print("读取全部:", f.read())
    
    # 逐行读取
    print("逐行读取:")
    with open('demo.txt', 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            print(f"  第{i}行: {line.strip()}")


def demo_pathlib():
    """pathlib路径操作"""
    print("\n=== pathlib路径操作 ===")
    
    # 创建Path对象
    p = Path('demo.txt')
    
    # 文件信息
    print(f"文件名: {p.name}")
    print(f"扩展名: {p.suffix}")
    print(f"是否存在: {p.exists()}")
    print(f"文件大小: {p.stat().st_size} 字节")
    
    # 创建目录
    output_dir = Path('output/data')
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"创建目录: {output_dir}")
    
    # Path读写
    data_file = output_dir / 'data.json'
    data_file.write_text('{"status": "ok"}', encoding='utf-8')
    print(f"写入文件: {data_file}")
    print(f"读取内容: {data_file.read_text(encoding='utf-8')}")


def demo_json_config():
    """JSON配置文件处理"""
    print("\n=== JSON配置文件处理 ===")
    
    config_path = Path('output/config.json')
    
    # 写入配置
    config = {
        "app_name": "AI Agent",
        "version": "1.0.0",
        "settings": {
            "debug": True,
            "max_retries": 3
        }
    }
    
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"配置已保存: {config_path}")
    
    # 读取配置
    loaded = json.loads(config_path.read_text(encoding='utf-8'))
    print(f"应用名称: {loaded['app_name']}")
    print(f"调试模式: {loaded['settings']['debug']}")


def demo_file_search():
    """文件搜索"""
    print("\n=== 文件搜索 ===")
    
    # 查找当前目录的Python文件
    py_files = list(Path('.').glob('*.py'))
    print(f"当前目录Python文件: {len(py_files)} 个")
    for f in py_files[:3]:
        print(f"  - {f.name}")


if __name__ == '__main__':
    demo_file_basic()
    demo_pathlib()
    demo_json_config()
    demo_file_search()
    
    # 清理演示文件
    Path('demo.txt').unlink(missing_ok=True)
    print("\n演示完成！")