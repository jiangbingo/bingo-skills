#!/usr/bin/env node

/**
 * MCP Server 本地测试脚本
 * 用于验证所有 MCP 工具是否正常工作
 */

import { spawn } from 'child_process';

class MCPTester {
  constructor(serverPath) {
    this.serverPath = serverPath;
    this.server = null;
    this.messageId = 1;
  }

  async start() {
    console.log('🚀 Starting MCP Server...\n');
    this.server = spawn('node', [this.serverPath], {
      stdio: ['pipe', 'pipe', 'inherit'] // stderr goes to console
    });

    this.server.on('error', (err) => {
      console.error('❌ Failed to start server:', err);
      process.exit(1);
    });

    // 等待服务器启动
    await this.sleep(500);
  }

  async sendRequest(method, params = {}) {
    const request = {
      jsonrpc: '2.0',
      id: this.messageId++,
      method,
      params
    };

    const requestStr = JSON.stringify(request) + '\n';
    this.server.stdin.write(requestStr);

    return new Promise((resolve, reject) => {
      let responseBuffer = '';

      const timeout = setTimeout(() => {
        reject(new Error('Request timeout'));
      }, 30000);

      this.server.stdout.on('data', (data) => {
        responseBuffer += data.toString();
        const lines = responseBuffer.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const response = JSON.parse(line);
            if (response.id === request.id) {
              clearTimeout(timeout);
              resolve(response);
            }
          } catch (e) {
            // Ignore parsing errors
          }
        }
      });
    });
  }

  async testListTools() {
    console.log('📋 Testing tools/list...');

    const response = await this.sendRequest('tools/list');

    if (response.error) {
      console.error('❌ Error:', response.error);
      return false;
    }

    const tools = response.result.tools;
    console.log(`✓ Found ${tools.length} tools:\n`);

    tools.forEach(tool => {
      console.log(`  • ${tool.name}`);
      console.log(`    ${tool.description.substring(0, 80)}...`);
      console.log('');
    });

    return true;
  }

  async testCallTool(toolName, args = {}) {
    console.log(`🔧 Testing ${toolName}...`);
    console.log(`   Args:`, args);

    try {
      const response = await this.sendRequest('tools/call', {
        name: toolName,
        arguments: args
      });

      if (response.error) {
        console.error(`❌ Error:`, response.error);
        return false;
      }

      console.log(`✓ Success`);
      if (response.result.content) {
        const content = response.result.content[0];
        if (content && content.text) {
          console.log(`   Result:`, content.text.substring(0, 200) + '...');
        }
      }
      console.log('');
      return true;
    } catch (error) {
      console.error(`❌ Exception:`, error.message);
      return false;
    }
  }

  async runTests() {
    await this.start();

    // 测试 1: 列出所有工具
    const listResult = await this.testListTools();
    if (!listResult) {
      console.error('❌ Failed to list tools');
      await this.stop();
      process.exit(1);
    }

    // 测试 2: 获取历史记录（不需要网络）
    console.log('---\n');
    await this.testCallTool('get_history', { limit: 5 });

    // 测试 3: 获取统计信息（不需要网络）
    await this.testCallTool('get_stats', {});

    // 测试 4: 列出格式（需要真实URL，使用示例）
    console.log('---\n');
    console.log('⚠️  Skipping actual download tests (requires real URL)');
    console.log('    To test downloads, uncomment the lines below:\n');
    /*
    await this.testCallTool('list_formats', {
      url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    });
    */

    console.log('---\n');
    console.log('✅ All tests passed!');
    await this.stop();
  }

  async stop() {
    if (this.server) {
      this.server.stdin.end();
      await this.sleep(100);
      this.server.kill();
    }
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// 运行测试
const tester = new MCPTester('./dist/index.js');
tester.runTests().catch(error => {
  console.error('❌ Test failed:', error);
  process.exit(1);
});
