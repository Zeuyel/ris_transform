import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

/**
 * 获取评级系统列表（代理到后端 API 以获取完整的 levels 信息）
 * GET /api/rating-systems
 */
export async function GET() {
  try {
    // 代理到后端 API，后端会正确获取每个系统的 levels
    const response = await fetch(`${BACKEND_URL}/api/rating-systems`);
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('加载评级系统失败:', error);
    // 如果后端不可用，降级到本地配置（但没有 levels）
    try {
      const configPath = path.join(process.cwd(), '..', 'data', 'config.json');
      const configContent = await fs.readFile(configPath, 'utf-8');
      const config = JSON.parse(configContent);

      const ratingSystems = config.rating_systems || {};
      const items = Object.entries(ratingSystems).map(([id, info]: [string, any]) => ({
        id,
        name: info.name || id,
        description: info.description || '',
        levels: [], // 无法获取 levels
      }));

      return NextResponse.json({ items });
    } catch (fallbackError) {
      return NextResponse.json(
        { error: '加载评级系统失败', items: [] },
        { status: 500 }
      );
    }
  }
}

/**
 * 添加或更新评级系统
 * POST /api/rating-systems
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { id, name, description, filePath, attributeMapping } = body;

    if (!id || !name) {
      return NextResponse.json(
        { error: '请提供系统 ID 和名称' },
        { status: 400 }
      );
    }

    const configPath = path.join(process.cwd(), '..', 'data', 'config.json');
    const configContent = await fs.readFile(configPath, 'utf-8');
    const config = JSON.parse(configContent);

    // 更新 rating_systems
    if (!config.rating_systems) {
      config.rating_systems = {};
    }
    config.rating_systems[id] = {
      name,
      description: description || '',
    };

    // 更新 rating_file_paths（如果提供）
    if (filePath) {
      if (!config.rating_file_paths) {
        config.rating_file_paths = {};
      }
      config.rating_file_paths[id] = filePath;
    }

    // 更新 json_attribute_mapping（如果提供）
    if (attributeMapping) {
      if (!config.json_attribute_mapping) {
        config.json_attribute_mapping = {};
      }
      config.json_attribute_mapping[id] = attributeMapping;
    }

    // 写回文件
    await fs.writeFile(configPath, JSON.stringify(config, null, 4), 'utf-8');

    return NextResponse.json({ success: true, id });
  } catch (error) {
    console.error('保存评级系统失败:', error);
    return NextResponse.json(
      { error: '保存评级系统失败: ' + (error as Error).message },
      { status: 500 }
    );
  }
}

/**
 * 删除评级系统
 * DELETE /api/rating-systems
 */
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json({ error: '请提供系统 ID' }, { status: 400 });
    }

    const configPath = path.join(process.cwd(), '..', 'data', 'config.json');
    const configContent = await fs.readFile(configPath, 'utf-8');
    const config = JSON.parse(configContent);

    // 检查是否在使用
    const criteriaPath = path.join(process.cwd(), '..', 'data', 'criteria');
    const criteriaFiles = await fs.readdir(criteriaPath).catch(() => []);
    
    for (const file of criteriaFiles) {
      if (!file.endsWith('.json')) continue;
      const filePath = path.join(criteriaPath, file);
      const content = await fs.readFile(filePath, 'utf-8');
      const criteria = JSON.parse(content);
      
      if (criteria[id]) {
        return NextResponse.json(
          { error: `评级系统 ${id} 正在被标准 ${file} 使用，无法删除` },
          { status: 400 }
        );
      }
    }

    // 删除相关配置
    if (config.rating_systems) {
      delete config.rating_systems[id];
    }
    if (config.rating_file_paths) {
      delete config.rating_file_paths[id];
    }
    if (config.json_attribute_mapping) {
      delete config.json_attribute_mapping[id];
    }

    // 写回文件
    await fs.writeFile(configPath, JSON.stringify(config, null, 4), 'utf-8');

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('删除评级系统失败:', error);
    return NextResponse.json(
      { error: '删除评级系统失败: ' + (error as Error).message },
      { status: 500 }
    );
  }
}

