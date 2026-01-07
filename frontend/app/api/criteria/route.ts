import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

/**
 * 获取分类标准列表
 * GET /api/criteria
 */
export async function GET() {
  try {
    // 读取配置文件
    const configPath = path.join(process.cwd(), '..', 'data', 'config.json');
    const configContent = await fs.readFile(configPath, 'utf-8');
    const config = JSON.parse(configContent);

    // 读取分类标准
    const criteriaPath = path.join(process.cwd(), '..', 'data', 'criteria');
    const criteriaFiles = await fs.readdir(criteriaPath).catch(() => []);

    const items: { id: string; name: string; description: string }[] = [];

    // 从配置中获取预定义的分类标准
    if (config.selection_criteria) {
      for (const [id, criteria] of Object.entries(config.selection_criteria)) {
        items.push({
          id,
          name: id,
          description: `包含: ${Object.keys(criteria as object).join(', ')}`,
        });
      }
    }

    // 从 criteria 目录加载额外的分类标准
    for (const file of criteriaFiles) {
      if (!file.endsWith('.json')) continue;

      const id = path.basename(file, '.json');
      if (items.some((item) => item.id === id)) continue;

      try {
        const filePath = path.join(criteriaPath, file);
        const content = await fs.readFile(filePath, 'utf-8');
        const data = JSON.parse(content);

        items.push({
          id,
          name: data.name || id,
          description: data.description || '',
        });
      } catch {
        // 忽略无效文件
      }
    }

    return NextResponse.json({ items });
  } catch (error) {
    console.error('加载分类标准失败:', error);
    return NextResponse.json(
      { error: '加载分类标准失败', items: [] },
      { status: 500 }
    );
  }
}

