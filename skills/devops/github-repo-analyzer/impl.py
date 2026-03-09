import json
import subprocess
from datetime import datetime, timedelta
from collections import Counter

def fetch_repos():
    result = subprocess.run(
        'gh repo list --limit 1000 --json name,isFork,createdAt,updatedAt,pushedAt,diskUsage,stargazerCount,forkCount,primaryLanguage,description,url,visibility',
        shell=True,
        capture_output=True,
        text=True
    )

    # 检查命令是否成功执行
    if result.returncode != 0:
        print("⚠️  无法连接到 GitHub API（可能需要认证）")
        print("   提示: 运行 'gh auth login' 进行认证")
        return []

    # 检查输出是否为空
    if not result.stdout or result.stdout.strip() == '':
        print("ℹ️  未找到任何 GitHub 仓库")
        return []

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"❌ 解析 GitHub API 响应失败: {e}")
        print(f"   响应内容: {result.stdout[:200] if result.stdout else '(空)'}")
        return []

def generate_report(repos):
    now = datetime.now()
    six_months_ago = (now - timedelta(days=180)).strftime('%Y-%m-%d')
    one_year_ago = (now - timedelta(days=365)).strftime('%Y-%m-%d')
    
    fork_repos = [r for r in repos if r.get('isFork', False)]
    orig_repos = [r for r in repos if not r.get('isFork', False)]
    
    report = []
    report.append("=" * 140)
    report.append("GitHub 仓库分析报告")
    report.append(f"分析时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 140)
    report.append(f"总仓库数: {len(repos)}")
    report.append(f"  - Fork 项目: {len(fork_repos)}")
    report.append(f"  - 原始项目: {len(orig_repos)}")
    report.append("")
    
    report.append("=" * 140)
    report.append("📊 仓库类型分布")
    report.append("=" * 140)
    
    visibility = Counter(r.get('visibility', 'unknown') for r in repos)
    report.append("可见性:")
    for v, count in visibility.most_common():
        report.append(f"  - {v}: {count} 个")
    
    report.append("")
    report.append("语言分布 (Top 10):")
    langs = Counter((r.get('primaryLanguage') or {}).get('name', 'None') for r in repos)
    for lang, count in langs.most_common(10):
        report.append(f"  - {lang}: {count} 个")
    
    report.append("")
    report.append("=" * 140)
    report.append(f"🔴 Fork 项目详细分析 ({len(fork_repos)} 个)")
    report.append("=" * 140)
    
    fork_old = [r for r in fork_repos if r['updatedAt'][:10] < six_months_ago]
    fork_recent = [r for r in fork_repos if r['updatedAt'][:10] >= six_months_ago]
    
    report.append("时间分布:")
    report.append(f"  - 超过6个月未更新: {len(fork_old)} 个")
    report.append(f"  - 6个月内更新: {len(fork_recent)} 个")
    
    report.append("")
    report.append("活跃度分析:")
    fork_active = [r for r in fork_repos if r.get('stargazerCount', 0) > 0 or r.get('forkCount', 0) > 0]
    fork_inactive = [r for r in fork_repos if r.get('stargazerCount', 0) == 0 and r.get('forkCount', 0) == 0]
    report.append(f"  - 有 star 或 fork: {len(fork_active)} 个")
    report.append(f"  - 无 star 和 fork: {len(fork_inactive)} 个")
    
    fork_storage = sum(r.get('diskUsage', 0) for r in fork_repos)
    report.append(f"  - Fork 项目总存储: {fork_storage / 1024:.2f} GB")
    
    report.append("")
    report.append("=" * 140)
    report.append(f"🟢 原始项目详细分析 ({len(orig_repos)} 个)")
    report.append("=" * 140)
    
    orig_old = [r for r in orig_repos if r['updatedAt'][:10] < six_months_ago]
    orig_recent = [r for r in orig_repos if r['updatedAt'][:10] >= six_months_ago]
    
    report.append("时间分布:")
    report.append(f"  - 超过6个月未更新: {len(orig_old)} 个")
    report.append(f"  - 6个月内更新: {len(orig_recent)} 个")
    
    report.append("")
    report.append("活跃度分析:")
    orig_active = [r for r in orig_repos if r.get('stargazerCount', 0) > 0 or r.get('forkCount', 0) > 0]
    orig_inactive = [r for r in orig_repos if r.get('stargazerCount', 0) == 0 and r.get('forkCount', 0) == 0]
    report.append(f"  - 有 star 或 fork: {len(orig_active)} 个")
    report.append(f"  - 无 star 和 fork: {len(orig_inactive)} 个")
    
    orig_storage = sum(r.get('diskUsage', 0) for r in orig_repos)
    report.append(f"  - 原始项目总存储: {orig_storage / 1024:.2f} GB")
    
    report.append("")
    report.append("=" * 140)
    report.append("📈 原始项目列表（按更新时间排序）")
    report.append("=" * 140)
    report.append(f"{'项目名称':<30} {'更新日期':<12} {'⭐':<4} {'🍴':<4} {'语言':<15} {'描述'}")
    report.append("-" * 140)
    orig_sorted = sorted(orig_repos, key=lambda x: x['updatedAt'], reverse=True)
    for r in orig_sorted[:30]:
        updated = r['updatedAt'][:10]
        stars = r.get('stargazerCount', 0)
        forks_count = r.get('forkCount', 0)
        lang = (r.get('primaryLanguage') or {}).get('name', 'N/A')
        desc = (r.get('description') or 'N/A')[:40]
        report.append(f"{r['name']:<30} {updated:<12} {stars:<4} {forks_count:<4} {lang:<15} {desc}")
    
    report.append("")
    report.append("=" * 140)
    report.append("💾 存储空间总览")
    report.append("=" * 140)
    total_storage = fork_storage + orig_storage
    report.append(f"  - Fork 项目: {fork_storage / 1024:.2f} GB")
    report.append(f"  - 原始项目: {orig_storage / 1024:.2f} GB")
    report.append(f"  - 总计: {total_storage / 1024:.2f} GB")
    
    report.append("")
    report.append("=" * 140)
    report.append("🎯 清理建议")
    report.append("=" * 140)
    
    fork_cleanup_candidates = []
    for r in fork_repos:
        if r['updatedAt'][:10] < six_months_ago and r.get('stargazerCount', 0) == 0 and r.get('forkCount', 0) == 0:
            fork_cleanup_candidates.append(r)
    
    orig_cleanup_candidates = []
    for r in orig_repos:
        if r['updatedAt'][:10] < one_year_ago and r.get('stargazerCount', 0) == 0 and r.get('forkCount', 0) == 0 and r.get('diskUsage', 0) < 100:
            orig_cleanup_candidates.append(r)
    
    fork_storage_cleanup = sum(r.get('diskUsage', 0) for r in fork_cleanup_candidates)
    orig_storage_cleanup = sum(r.get('diskUsage', 0) for r in orig_cleanup_candidates)
    
    report.append("Fork 项目清理:")
    fork_pct = (len(fork_cleanup_candidates) / len(fork_repos) * 100) if len(fork_repos) > 0 else 0
    report.append(f"  - 可删除数量: {len(fork_cleanup_candidates)} 个 (占总 fork: {fork_pct:.1f}%)")
    report.append(f"  - 可释放空间: {fork_storage_cleanup / 1024:.2f} GB")

    report.append("")
    report.append("原始项目清理:")
    orig_pct = (len(orig_cleanup_candidates) / len(orig_repos) * 100) if len(orig_repos) > 0 else 0
    report.append(f"  - 可删除数量: {len(orig_cleanup_candidates)} 个 (占总原始: {orig_pct:.1f}%)")
    report.append(f"  - 可释放空间: {orig_storage_cleanup / 1024:.2f} GB")
    
    report.append("")
    report.append("总计清理:")
    report.append(f"  - 可删除数量: {len(fork_cleanup_candidates) + len(orig_cleanup_candidates)} 个")
    report.append(f"  - 可释放空间: {(fork_storage_cleanup + orig_storage_cleanup) / 1024:.2f} GB")
    report.append(f"  - 清理后剩余: {len(repos) - len(fork_cleanup_candidates) - len(orig_cleanup_candidates)} 个")
    
    report.append("")
    report.append("=" * 140)
    report.append("✅ 活跃项目推荐保留")
    report.append("=" * 140)
    
    active_forks = [r for r in fork_repos if r['updatedAt'][:10] >= six_months_ago or r.get('stargazerCount', 0) > 0 or r.get('forkCount', 0) > 0]
    report.append(f"Fork 项目（{len(active_forks)} 个）:")
    for r in active_forks[:10]:
        updated = r['updatedAt'][:10]
        stars = r.get('stargazerCount', 0)
        forks_count = r.get('forkCount', 0)
        lang = (r.get('primaryLanguage') or {}).get('name', 'N/A')
        report.append(f"  - {r['name']:<30} | 更新: {updated} | ⭐{stars} | 🍴{forks_count} | {lang}")
    
    active_orig = [r for r in orig_repos if r['updatedAt'][:10] >= six_months_ago or r.get('stargazerCount', 0) > 0 or r.get('forkCount', 0) > 0]
    report.append("")
    report.append(f"原始项目（{len(active_orig)} 个）:")
    for r in active_orig[:10]:
        updated = r['updatedAt'][:10]
        stars = r.get('stargazerCount', 0)
        forks_count = r.get('forkCount', 0)
        lang = (r.get('primaryLanguage') or {}).get('name', 'N/A')
        desc = (r.get('description') or 'N/A')[:35]
        report.append(f"  - {r['name']:<30} | 更新: {updated} | ⭐{stars} | 🍴{forks_count} | {desc}")
    
    return '\n'.join(report)

def save_report(report, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

def main():
    print("🔍 正在获取 GitHub 仓库数据...")
    repos = fetch_repos()
    print(f"✅ 成功获取 {len(repos)} 个仓库")
    
    print("📊 正在分析仓库数据...")
    report = generate_report(repos)
    
    output_file = 'repos_analysis_report.txt'
    print("📝 正在生成分析报告...")
    save_report(report, output_file)
    print(f"✅ 报告已保存到: {output_file}")
    
    print("\n" + "=" * 60)
    print("📋 分析摘要")
    print("=" * 60)
    print(f"  总仓库数: {len(repos)}")
    fork_repos = [r for r in repos if r.get('isFork', False)]
    orig_repos = [r for r in repos if not r.get('isFork', False)]
    print(f"  Fork 项目: {len(fork_repos)}")
    print(f"  原始项目: {len(orig_repos)}")
    print(f"  报告文件: {output_file}")

if __name__ == '__main__':
    main()
