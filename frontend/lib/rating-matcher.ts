import type { RisEntry, SelectionCriteria } from '@/types';

/**
 * 评级数据项
 */
interface RatingDataItem {
  [key: string]: string | number | null;
}

/**
 * 评级数据缓存
 */
const ratingDataCache: Map<string, RatingDataItem[]> = new Map();

/**
 * 加载评级数据
 */
export async function loadRatingData(
  systemId: string,
  filePath: string
): Promise<RatingDataItem[]> {
  if (ratingDataCache.has(systemId)) {
    return ratingDataCache.get(systemId)!;
  }

  try {
    const response = await fetch(filePath);
    if (!response.ok) {
      console.warn(`无法加载评级数据: ${filePath}`);
      return [];
    }
    const data = await response.json();
    ratingDataCache.set(systemId, data);
    return data;
  } catch (error) {
    console.error(`加载评级数据失败: ${systemId}`, error);
    return [];
  }
}

/**
 * 查询期刊评级
 */
export function getJournalRating(
  journalName: string,
  ratingData: RatingDataItem[],
  titleField: string,
  levelField: string,
  typeField?: string
): { level: string; type?: string } | null {
  const lowerJournalName = journalName.toLowerCase();

  for (const item of ratingData) {
    const itemTitle = String(item[titleField] || '').toLowerCase();

    if (itemTitle === lowerJournalName) {
      const level = String(item[levelField] || '');
      const type = typeField ? String(item[typeField] || '') : undefined;

      return { level, type };
    }
  }

  return null;
}

/**
 * 检查条目是否匹配分类标准
 */
export function matchesCriteria(
  ratings: Record<string, string>,
  criteria: SelectionCriteria
): boolean {
  for (const [systemId, requiredLevels] of Object.entries(criteria)) {
    const entryRating = ratings[systemId];

    if (!entryRating || entryRating === 'Not Found') {
      continue;
    }

    // 检查是否匹配任一要求的等级
    const matched = requiredLevels.some((level) => {
      const levelStr = String(level);
      return entryRating === levelStr || entryRating.startsWith(levelStr);
    });

    if (matched) {
      return true;
    }
  }

  return false;
}

/**
 * 根据分类标准筛选条目
 */
export function filterEntriesByCriteria(
  entries: RisEntry[],
  allRatings: Map<string, Record<string, string>>,
  criteria: SelectionCriteria
): RisEntry[] {
  return entries.filter((entry) => {
    const title = entry.TI?.[0];
    if (!title) return false;

    const ratings = allRatings.get(title.toLowerCase());
    if (!ratings) return false;

    return matchesCriteria(ratings, criteria);
  });
}

/**
 * 批量获取所有条目的评级信息
 */
export async function batchGetRatings(
  entries: RisEntry[],
  ratingConfigs: {
    systemId: string;
    data: RatingDataItem[];
    titleField: string;
    levelField: string;
    typeField?: string;
  }[]
): Promise<Map<string, Record<string, string>>> {
  const ratingsMap = new Map<string, Record<string, string>>();

  for (const entry of entries) {
    const journalName = entry.T2?.[0];
    const title = entry.TI?.[0];

    if (!journalName || !title) continue;

    const ratings: Record<string, string> = {};

    for (const config of ratingConfigs) {
      const rating = getJournalRating(
        journalName,
        config.data,
        config.titleField,
        config.levelField,
        config.typeField
      );

      if (rating) {
        // CCF 特殊处理：等级+类型
        if (config.systemId === 'CCF' && rating.type) {
          ratings[config.systemId] = `${rating.level}${rating.type}`;
        } else {
          ratings[config.systemId] = rating.level;
        }
      } else {
        ratings[config.systemId] = 'Not Found';
      }
    }

    ratingsMap.set(title.toLowerCase(), ratings);
  }

  return ratingsMap;
}

