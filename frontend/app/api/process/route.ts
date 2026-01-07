import { NextRequest, NextResponse } from 'next/server';
import { parseRis, deduplicateEntries, entriesToRis } from '@/lib/ris-parser';
import { promises as fs } from 'fs';
import path from 'path';
import JSZip from 'jszip';

interface RatingDataItem {
  [key: string]: string | number | null;
}

interface SelectionCriteria {
  [systemId: string]: (string | number)[];
}

interface ProfileData {
  name: string;
  criteria_sets: Record<string, SelectionCriteria>;
}

/**
 * 处理 RIS 文件
 * POST /api/process
 */
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    const selectedProfiles = formData.getAll('selected_profiles') as string[];
    const deduplicate = formData.get('deduplicate') !== 'false';

    if (!file) {
      return NextResponse.json({ error: '请上传文件' }, { status: 400 });
    }

    if (selectedProfiles.length === 0) {
      return NextResponse.json({ error: '请选择至少一个分类标准' }, { status: 400 });
    }

    // 读取文件内容
    const content = await file.text();
    let entries = parseRis(content);

    // 去重
    if (deduplicate) {
      entries = deduplicateEntries(entries);
    }

    // 加载配置
    const configPath = path.join(process.cwd(), '..', 'data', 'config.json');
    const configContent = await fs.readFile(configPath, 'utf-8');
    const config = JSON.parse(configContent);

    // 加载评级数据
    const ratingData: Map<string, RatingDataItem[]> = new Map();
    const ratingFilePaths = config.rating_file_paths || {};
    const jsonAttributeMapping = config.json_attribute_mapping || {};

    for (const [systemId, filePath] of Object.entries(ratingFilePaths)) {
      try {
        // 规范化路径（处理 Windows 反斜杠）
        const normalizedPath = (filePath as string).replace(/\\/g, '/');
        const fullPath = path.join(process.cwd(), '..', 'data', normalizedPath);
        const data = JSON.parse(await fs.readFile(fullPath, 'utf-8'));
        ratingData.set(systemId, data);
      } catch (e) {
        console.warn(`无法加载评级数据: ${systemId}`, e);
      }
    }

    // 处理每个条目，获取评级
    const entryRatings = new Map<string, Record<string, string>>();

    for (const entry of entries) {
      const journalName = entry.T2?.[0];
      const title = entry.TI?.[0];
      if (!journalName || !title) continue;

      const ratings: Record<string, string> = {};

      for (const [systemId, data] of ratingData) {
        const mapping = jsonAttributeMapping[systemId] || {};
        const titleField = mapping.paper_name || 'Paper_name';
        const levelField = mapping.level || 'Level';
        const typeField = mapping.type;

        const lowerJournal = journalName.toLowerCase();
        const found = data.find(
          (item) => String(item[titleField] || '').toLowerCase() === lowerJournal
        );

        if (found) {
          const level = String(found[levelField] || '');
          const type = typeField ? String(found[typeField] || '') : '';
          ratings[systemId] = systemId === 'CCF' && type ? `${level}${type}` : level;
        } else {
          ratings[systemId] = 'Not Found';
        }
      }

      entryRatings.set(title.toLowerCase(), ratings);
    }

    // 创建 ZIP
    const zip = new JSZip();
    const profilesDir = path.join(process.cwd(), '..', 'data', 'profiles');

    console.log('=== 调试信息 ===');
    console.log('总条目数:', entries.length);
    console.log('有评级的条目数:', entryRatings.size);
    console.log('选中的 Profiles:', selectedProfiles);
    console.log('Profiles 目录:', profilesDir);

    // 处理每个选中的 Profile
    for (const profileId of selectedProfiles) {
      // 加载 profile 文件
      let profileData: ProfileData;
      try {
        const profilePath = path.join(profilesDir, `${profileId}.json`);
        console.log('尝试加载 Profile:', profilePath);
        const profileContent = await fs.readFile(profilePath, 'utf-8');
        profileData = JSON.parse(profileContent);
        console.log('Profile 加载成功:', profileData.name, 'CriteriaSets:', Object.keys(profileData.criteria_sets));
      } catch (e) {
        console.warn(`无法加载 Profile: ${profileId}`, e);
        continue;
      }

      // 为该 Profile 创建一个文件夹
      const profileFolder = zip.folder(profileData.name) || zip;

      // 处理 Profile 中的每个 CriteriaSet
      for (const [criteriaSetName, criteria] of Object.entries(profileData.criteria_sets)) {
        console.log(`处理 CriteriaSet: ${criteriaSetName}`, criteria);

        const filteredEntries = entries.filter((entry) => {
          const title = entry.TI?.[0];
          if (!title) return false;

          const ratings = entryRatings.get(title.toLowerCase());
          if (!ratings) return false;

          // 检查是否匹配任一系统的要求
          for (const [systemId, requiredLevels] of Object.entries(criteria)) {
            const entryRating = ratings[systemId];
            if (!entryRating || entryRating === 'Not Found') continue;

            const matched = requiredLevels.some((level) => {
              const levelStr = String(level);
              return entryRating === levelStr || entryRating.startsWith(levelStr);
            });

            if (matched) return true;
          }

          return false;
        });

        console.log(`CriteriaSet ${criteriaSetName} 匹配条目数:`, filteredEntries.length);

        if (filteredEntries.length > 0) {
          const risContent = entriesToRis(filteredEntries);
          profileFolder.file(`${criteriaSetName}.ris`, risContent);
        }
      }
    }

    const zipBuffer = await zip.generateAsync({ type: 'nodebuffer' });
    const filename = `${path.basename(file.name, '.ris')}_outputs.zip`;

    return new NextResponse(zipBuffer, {
      headers: {
        'Content-Type': 'application/zip',
        'Content-Disposition': `attachment; filename="${filename}"`,
      },
    });
  } catch (error) {
    console.error('处理失败:', error);
    return NextResponse.json(
      { error: '处理失败: ' + (error as Error).message },
      { status: 500 }
    );
  }
}

