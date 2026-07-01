#!/usr/bin/env python3
"""
deploy.py — 配件看板部署到 Gitee Pages
被 parts_monitor.py 和 auto_update.py 调用，每次生成HTML后自动推送到Gitee。
"""
import os, sys, subprocess, shutil
from datetime import datetime

GITEE_REMOTE = "https://gitee.com/lu-pin-8888/peijian-kanban.git"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def deploy(html_path):
    """
    将生成的HTML复制到Gitee Pages仓库并推送。
    返回 (success: bool, url: str)
    """
    local_index = os.path.join(REPO_DIR, "index.html")
    
    # 1. 复制HTML为 index.html
    try:
        shutil.copy2(html_path, local_index)
        print(f"  [Gitee] HTML已复制: {html_path} -> {local_index}")
    except Exception as e:
        print(f"  [Gitee ERR] 复制失败: {e}")
        return False, ""
    
    # 2. Git add + commit + push
    try:
        os.chdir(REPO_DIR)
        
        # 确保是git仓库
        subprocess.run(["git", "rev-parse", "--git-dir"], 
                       capture_output=True, check=True)
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        subprocess.run(["git", "add", "index.html"], 
                       capture_output=True, check=True)
        
        # 检查是否有变更
        status = subprocess.run(["git", "diff", "--cached", "--quiet", "index.html"], 
                                capture_output=True)
        if status.returncode == 0:
            print(f"  [Gitee] 无变更，跳过推送")
            return True, "https://lu-pin-8888.gitee.io/peijian-kanban/"
        
        subprocess.run(["git", "commit", "-m", f"更新配件看板 {now_str}"],
                       capture_output=True, check=True)
        
        push_result = subprocess.run(["git", "push", "origin", "master"],
                                     capture_output=True, text=True, timeout=30)
        if push_result.returncode != 0:
            stderr = push_result.stderr or push_result.stdout
            print(f"  [Gitee ERR] 推送失败: {stderr.strip()}")
            return False, ""
        
        print(f"  [Gitee] 推送成功!")
        return True, "https://lu-pin-8888.gitee.io/peijian-kanban/"
        
    except subprocess.CalledProcessError as e:
        print(f"  [Gitee ERR] Git操作失败: {e}")
        return False, ""
    except Exception as e:
        print(f"  [Gitee ERR] 部署异常: {e}")
        return False, ""


def setup_repo():
    """首次初始化本地仓库"""
    os.chdir(REPO_DIR)
    
    # 检查是否已经是git仓库
    result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                            capture_output=True)
    if result.returncode == 0:
        print("  [Gitee] git仓库已存在")
        return True
    
    # 初始化
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "remote", "add", "origin", GITEE_REMOTE], check=True)
    
    # 创建初始提交
    readme = os.path.join(REPO_DIR, "README.md")
    with open(readme, "w", encoding="utf-8") as f:
        f.write("# 配件到货监控看板\n\n东莞腾达红旗体验中心\n")
    subprocess.run(["git", "add", "README.md"], check=True)
    subprocess.run(["git", "commit", "-m", "初始化Gitee Pages"], check=True)
    
    print("  [Gitee] 仓库初始化完成")
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python deploy.py <html文件路径>")
        print("      python deploy.py --setup  (首次初始化)")
        sys.exit(1)
    
    if sys.argv[1] == "--setup":
        setup_repo()
    else:
        ok, url = deploy(sys.argv[1])
        if ok:
            print(f"  Gitee Pages: {url}")
