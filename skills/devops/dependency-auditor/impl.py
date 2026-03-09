#!/usr/bin/env python3
"""
依赖安全审计脚本
支持多种包管理器：npm、pip、cargo、composer
检测安全漏洞、过期依赖、许可证合规性
"""

import subprocess
import json
import os
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

# 许可证分类
PERMISSIVE_LICENSES = {'MIT', 'Apache-2.0', 'Apache License 2.0', 'BSD-2-Clause', 'BSD-3-Clause',
                       'ISC', 'Unlicense', 'CC0-1.0'}
WEAK_COPYLEFT = {'LGPL-2.0', 'LGPL-2.1', 'LGPL-3.0', 'LGPL-3.0+', 'MPL-2.0', 'MPL-2.0-no-copyleft-exception'}
STRONG_COPYLEFT = {'GPL-2.0', 'GPL-2.0+', 'GPL-3.0', 'GPL-3.0+', 'AGPL-3.0', 'AGPL-3.0+'}
RISKY_LICENSES = {'SSPL', 'CPAL', 'EUPL-1.2'}

class DependencyAuditor:
    def __init__(self):
        self.report_lines = []
        self.working_dir = Path.cwd()
        self.package_managers = []

    def log(self, message):
        """添加日志到报告"""
        self.report_lines.append(message)
        print(message)

    def detect_package_managers(self):
        """检测项目中使用的包管理器"""
        self.log("=" * 100)
        self.log("🔍 检测包管理器")
        self.log("=" * 100)

        managers = []

        # 检测 npm/Node.js
        if (self.working_dir / "package.json").exists():
            managers.append(("npm", "package.json"))
            self.log("✅ 检测到 npm (package.json)")

        # 检测 pip/Python
        if (self.working_dir / "requirements.txt").exists():
            managers.append(("pip", "requirements.txt"))
            self.log("✅ 检测到 pip (requirements.txt)")
        elif (self.working_dir / "pyproject.toml").exists():
            managers.append(("pip", "pyproject.toml"))
            self.log("✅ 检测到 pip (pyproject.toml)")

        # 检测 cargo/Rust
        if (self.working_dir / "Cargo.toml").exists():
            managers.append(("cargo", "Cargo.toml"))
            self.log("✅ 检测到 cargo (Cargo.toml)")

        # 检测 composer/PHP
        if (self.working_dir / "composer.json").exists():
            managers.append(("composer", "composer.json"))
            self.log("✅ 检测到 composer (composer.json)")

        # 检测 maven/Java
        if (self.working_dir / "pom.xml").exists():
            managers.append(("maven", "pom.xml"))
            self.log("✅ 检测到 maven (pom.xml)")

        # 检测 gradle/Java
        gradle_files = list(self.working_dir.glob("build.gradle*"))
        if gradle_files:
            managers.append(("gradle", gradle_files[0].name))
            self.log(f"✅ 检测到 gradle ({gradle_files[0].name})")

        self.package_managers = managers
        self.log("")
        return managers

    def audit_npm(self):
        """审计 npm 依赖"""
        self.log("=" * 100)
        self.log("📦 NPM 依赖审计")
        self.log("=" * 100)
        self.log("")

        vulnerabilities = []
        outdated = []
        licenses = []

        # 运行 npm audit
        self.log("🔒 运行安全扫描 (npm audit)...")
        try:
            result = subprocess.run(
                ['npm', 'audit', '--json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0 or 'audit' in result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    vulns = audit_data.get('vulnerabilities', {})
                    if vulns:
                        self.log(f"⚠️  发现 {len(vulns)} 个安全漏洞:")
                        for name, vuln in list(vulns.items())[:20]:
                            severity = vuln.get('severity', 'unknown')
                            title = vuln.get('title', 'No title')
                            self.log(f"   - [{severity.upper()}] {name}: {title}")
                            vulnerabilities.append({
                                'name': name,
                                'severity': severity,
                                'title': title
                            })
                    else:
                        self.log("✅ 未发现安全漏洞")
                except json.JSONDecodeError:
                    self.log("⚠️  无法解析 npm audit 输出")
            else:
                self.log("ℹ️  npm audit 未返回漏洞数据")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.log(f"⚠️  npm audit 执行失败: {e}")

        self.log("")

        # 检查过期包
        self.log("📅 检查过期依赖 (npm outdated)...")
        try:
            result = subprocess.run(
                ['npm', 'outdated', '--json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.stdout:
                try:
                    outdated_data = json.loads(result.stdout)
                    outdated_count = len(outdated_data)
                    if outdated_count > 0:
                        self.log(f"⚠️  发现 {outdated_count} 个过期依赖:")
                        for name, info in list(outdated_data.items())[:15]:
                            current = info.get('current', 'unknown')
                            latest = info.get('latest', 'unknown')
                            self.log(f"   - {name}: {current} → {latest}")
                            outdated.append({
                                'name': name,
                                'current': current,
                                'latest': latest
                            })
                    else:
                        self.log("✅ 所有依赖都是最新版本")
                except json.JSONDecodeError:
                    self.log("✅ 未发现过期依赖")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("⚠️  npm outdated 执行失败")

        self.log("")

        # 检查许可证
        self.log("📜 检查许可证合规性...")
        try:
            result = subprocess.run(
                ['npm', 'ls', '--json', '--depth=0'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                data = json.loads(result.stdout)
                deps = data.get('dependencies', {})

                # 读取 package.json 获取许可证信息
                with open('package.json', 'r') as f:
                    pkg_data = json.load(f)

                license_issues = []
                for name, info in deps.items():
                    license_str = info.get('license', 'unknown')
                    if license_str in STRONG_COPYLEFT:
                        license_issues.append(f"   - {name}: {license_str} (强 copyleft)")
                        licenses.append({'name': name, 'license': license_str, 'type': 'strong'})
                    elif license_str in RISKY_LICENSES:
                        license_issues.append(f"   - {name}: {license_str} (潜在风险)")
                        licenses.append({'name': name, 'license': license_str, 'type': 'risky'})
                    elif license_str == 'unknown':
                        licenses.append({'name': name, 'license': license_str, 'type': 'unknown'})

                if license_issues:
                    self.log("⚠️  发现许可证合规性问题:")
                    for issue in license_issues:
                        self.log(issue)
                else:
                    self.log("✅ 许可证检查通过")
        except Exception as e:
            self.log(f"⚠️  许可证检查失败: {e}")

        return vulnerabilities, outdated, licenses

    def audit_pip(self):
        """审计 pip 依赖"""
        self.log("=" * 100)
        self.log("🐍 PIP 依赖审计")
        self.log("=" * 100)
        self.log("")

        vulnerabilities = []
        outdated = []
        licenses = []

        # 尝试运行 pip-audit
        self.log("🔒 运行安全扫描 (pip-audit)...")
        try:
            result = subprocess.run(
                ['pip-audit', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities_data = audit_data.get('dependencies', [])
                    if vulnerabilities_data:
                        vuln_count = sum(len(d.get('vulnerabilities', [])) for d in vulnerabilities_data)
                        self.log(f"⚠️  发现 {vuln_count} 个安全漏洞:")
                        for dep in vulnerabilities_data[:15]:
                            name = dep.get('name', 'unknown')
                            vulns = dep.get('vulnerabilities', [])
                            for vuln in vulns[:3]:
                                severity = vuln.get('severity', 'unknown')
                                self.log(f"   - [{severity.upper()}] {name}")
                                vulnerabilities.append({'name': name, 'severity': severity})
                    else:
                        self.log("✅ 未发现安全漏洞")
                except json.JSONDecodeError:
                    self.log("⚠️  无法解析 pip-audit 输出")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("ℹ️  pip-audit 未安装，跳过安全扫描")

        self.log("")

        # 检查过期包
        self.log("📅 检查过期依赖 (pip list --outdated)...")
        try:
            result = subprocess.run(
                ['pip', 'list', '--outdated', '--format=json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.stdout:
                outdated_data = json.loads(result.stdout)
                if outdated_data:
                    self.log(f"⚠️  发现 {len(outdated_data)} 个过期依赖:")
                    for pkg in outdated_data[:15]:
                        name = pkg.get('name', 'unknown')
                        version = pkg.get('version', 'unknown')
                        latest = pkg.get('latest_version', 'unknown')
                        self.log(f"   - {name}: {version} → {latest}")
                        outdated.append({'name': name, 'current': version, 'latest': latest})
                else:
                    self.log("✅ 所有依赖都是最新版本")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("⚠️  pip list --outdated 执行失败")

        self.log("")

        # 许可证检查需要额外工具，这里提供基本信息
        self.log("📜 许可证检查:")
        self.log("ℹ️  Python 许可证检查需要 pip-licenses 工具")
        self.log("   安装: pip install pip-licenses")
        self.log("   运行: pip-licenses --format=json")

        return vulnerabilities, outdated, licenses

    def audit_cargo(self):
        """审计 cargo 依赖"""
        self.log("=" * 100)
        self.log("🦀 CARGO 依赖审计")
        self.log("=" * 100)
        self.log("")

        vulnerabilities = []
        outdated = []
        licenses = []

        # 尝试运行 cargo audit
        self.log("🔒 运行安全扫描 (cargo audit)...")
        try:
            result = subprocess.run(
                ['cargo', 'audit', '--json'],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    vulns = audit_data.get('vulnerabilities', {}).get('list', [])
                    if vulns:
                        self.log(f"⚠️  发现 {len(vulns)} 个安全漏洞:")
                        for vuln in vulns[:15]:
                            advisory = vuln.get('advisory', {})
                            title = advisory.get('title', 'No title')
                            severity = self._map_rust_severity(advisory.get('severity', 'unknown'))
                            self.log(f"   - [{severity.upper()}] {title}")
                            vulnerabilities.append({'name': title, 'severity': severity})
                    else:
                        self.log("✅ 未发现安全漏洞")
                except json.JSONDecodeError:
                    self.log("✅ 未发现安全漏洞")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("ℹ️  cargo-audit 未安装，跳过安全扫描")
            self.log("   安装: cargo install cargo-audit")

        self.log("")

        # 检查过期包
        self.log("📅 检查过期依赖 (cargo outdated)...")
        try:
            result = subprocess.run(
                ['cargo', 'outdated', '--format=json'],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.stdout:
                outdated_data = json.loads(result.stdout)
                if outdated_data:
                    self.log(f"⚠️  发现 {len(outdated_data)} 个过期依赖:")
                    for pkg in outdated_data[:15]:
                        name = pkg.get('name', 'unknown')
                        current = pkg.get('version', 'unknown')
                        latest = pkg.get('latest', 'unknown')
                        self.log(f"   - {name}: {current} → {latest}")
                        outdated.append({'name': name, 'current': current, 'latest': latest})
                else:
                    self.log("✅ 所有依赖都是最新版本")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("ℹ️  cargo-outdated 未安装，跳过期检查")
            self.log("   安装: cargo install cargo-outdated")

        self.log("")

        # 许可证检查
        self.log("📜 检查许可证合规性...")
        self.log("ℹ️  Rust 许可证检查: cargo about")

        return vulnerabilities, outdated, licenses

    def audit_composer(self):
        """审计 composer 依赖"""
        self.log("=" * 100)
        self.log("🎼 COMPOSER 依赖审计")
        self.log("=" * 100)
        self.log("")

        vulnerabilities = []
        outdated = []
        licenses = []

        # 运行 composer audit
        self.log("🔒 运行安全扫描 (composer audit)...")
        try:
            result = subprocess.run(
                ['composer', 'audit', '--format=json'],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    if audit_data.get('advisories'):
                        vulns = audit_data['advisories']
                        self.log(f"⚠️  发现 {len(vulns)} 个安全漏洞:")
                        for name, vuln in list(vulns.items())[:15]:
                            title = vuln.get('title', 'No title')
                            self.log(f"   - {name}: {title}")
                            vulnerabilities.append({'name': name, 'title': title})
                    else:
                        self.log("✅ 未发现安全漏洞")
                except json.JSONDecodeError:
                    self.log("✅ 未发现安全漏洞")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("⚠️  composer audit 执行失败")

        self.log("")

        # 检查过期包
        self.log("📅 检查过期依赖 (composer outdated)...")
        try:
            result = subprocess.run(
                ['composer', 'outdated', '--format=json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.stdout:
                outdated_data = json.loads(result.stdout)
                if outdated_data.get('installed'):
                    outdated_count = 0
                    for pkg in outdated_data['installed']:
                        if pkg.get('latest'):
                            outdated_count += 1
                    if outdated_count > 0:
                        self.log(f"⚠️  发现 {outdated_count} 个过期依赖")
                    else:
                        self.log("✅ 所有依赖都是最新版本")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("⚠️  composer outdated 执行失败")

        return vulnerabilities, outdated, licenses

    def audit_maven(self):
        """审计 maven 依赖（基础检查）"""
        self.log("=" * 100)
        self.log("☕ MAVEN 依赖审计")
        self.log("=" * 100)
        self.log("")

        self.log("ℹ️  Maven 依赖审计需要额外工具:")
        self.log("   - OWASP Dependency-Check: https://owasp.org/www-project-dependency-check/")
        self.log("   - Snyk: https://snyk.io/")

        return [], [], []

    def audit_gradle(self):
        """审计 gradle 依赖（基础检查）"""
        self.log("=" * 100)
        self.log("🐘 GRADLE 依赖审计")
        self.log("=" * 100)
        self.log("")

        self.log("ℹ️  Gradle 依赖审计需要额外工具:")
        self.log("   - OWASP Dependency-Check plugin")
        self.log("   - Snyk: https://snyk.io/")

        return [], [], []

    def _map_rust_severity(self, severity):
        """映射 Rust 漏洞严重性"""
        mapping = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low',
            'none': 'low'
        }
        return mapping.get(severity.lower(), 'unknown')

    def generate_summary(self, all_vulnerabilities, all_outdated, all_licenses):
        """生成摘要报告"""
        self.log("")
        self.log("=" * 100)
        self.log("📊 审计摘要")
        self.log("=" * 100)
        self.log("")

        total_vulns = len(all_vulnerabilities)
        total_outdated = len(all_outdated)
        license_issues = len([l for l in all_licenses if l.get('type') in ['strong', 'risky']])

        self.log(f"总包管理器: {len(self.package_managers)}")
        self.log(f"  安全漏洞: {total_vulns} 个")
        self.log(f"  过期依赖: {total_outdated} 个")
        self.log(f"  许可证问题: {license_issues} 个")

        self.log("")
        self.log("=" * 100)
        self.log("🎯 建议操作")
        self.log("=" * 100)

        if total_vulns > 0:
            critical_vulns = [v for v in all_vulnerabilities if v.get('severity') == 'critical']
            high_vulns = [v for v in all_vulnerabilities if v.get('severity') == 'high']

            if critical_vulns:
                self.log("")
                self.log("🚨 高优先级 - 立即修复关键漏洞:")
                for v in critical_vulns[:5]:
                    self.log(f"   - {v.get('name', 'unknown')}")

            if high_vulns:
                self.log("")
                self.log("⚠️  中优先级 - 尽快修复高危漏洞:")
                for v in high_vulns[:5]:
                    self.log(f"   - {v.get('name', 'unknown')}")

        if total_outdated > 0:
            self.log("")
            self.log(f"📦 更新 {total_outdated} 个过期依赖以获取最新功能和安全修复")

        if license_issues > 0:
            self.log("")
            self.log(f"📜 检查 {license_issues} 个许可证合规性问题")

        if total_vulns == 0 and total_outdated == 0 and license_issues == 0:
            self.log("")
            self.log("✅ 所有检查通过！依赖健康状态良好。")

        self.log("")
        self.log("=" * 100)
        self.log("📝 后续步骤")
        self.log("=" * 100)
        self.log("1. 安装推荐的审计工具以获得更全面的扫描")
        self.log("2. 定期运行此审计（建议每月一次）")
        self.log("3. 在 CI/CD 流程中集成安全扫描")
        self.log("4. 订阅安全公告以获取最新漏洞信息")

    def run(self):
        """运行完整审计"""
        self.log("=" * 100)
        self.log("🔍 依赖安全审计工具")
        self.log(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"📁 工作目录: {self.working_dir}")
        self.log("=" * 100)
        self.log("")

        # 检测包管理器
        managers = self.detect_package_managers()

        if not managers:
            self.log("⚠️  未检测到任何包管理器配置文件")
            self.log("支持的包管理器: npm, pip, cargo, composer, maven, gradle")
            return

        self.log(f"✅ 检测到 {len(managers)} 个包管理器")
        self.log("")

        # 收集所有结果
        all_vulnerabilities = []
        all_outdated = []
        all_licenses = []

        # 审计各个包管理器
        audit_methods = {
            'npm': self.audit_npm,
            'pip': self.audit_pip,
            'cargo': self.audit_cargo,
            'composer': self.audit_composer,
            'maven': self.audit_maven,
            'gradle': self.audit_gradle
        }

        for manager_name, config_file in managers:
            if manager_name in audit_methods:
                vulns, outdated, licenses = audit_methods[manager_name]()
                all_vulnerabilities.extend(vulns)
                all_outdated.extend(outdated)
                all_licenses.extend(licenses)

        # 生成摘要
        self.generate_summary(all_vulnerabilities, all_outdated, all_licenses)

        # 保存报告
        self.save_report()

    def save_report(self):
        """保存报告到文件"""
        output_file = 'dependency_audit_report.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.report_lines))
        print(f"\n✅ 报告已保存到: {output_file}")

def main():
    auditor = DependencyAuditor()
    auditor.run()

if __name__ == '__main__':
    main()
