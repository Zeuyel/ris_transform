import type { RisEntry } from '@/types';

/**
 * 解析 RIS 文件内容
 * @param content RIS 文件文本内容
 * @returns 解析后的条目列表
 */
export function parseRis(content: string): RisEntry[] {
  const entries: RisEntry[] = [];
  let currentEntry: RisEntry = {};

  const lines = content.split('\n');

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) continue;

    // 条目结束标记
    if (line === 'ER  -') {
      if (Object.keys(currentEntry).length > 0) {
        // 初始化自定义字段
        currentEntry.C1 = [];
        currentEntry.C2 = [];
        currentEntry.LB = [];
        entries.push(currentEntry);
        currentEntry = {};
      }
      continue;
    }

    // 解析标签和值 (格式: XX  - value)
    if (line.length > 6) {
      const tag = line.substring(0, 2);
      const value = line.substring(6).trim();

      if (!currentEntry[tag]) {
        currentEntry[tag] = [];
      }
      currentEntry[tag]!.push(value);
    }
  }

  // 处理最后一个条目（如果没有 ER 结束标记）
  if (Object.keys(currentEntry).length > 0) {
    currentEntry.C1 = [];
    currentEntry.C2 = [];
    currentEntry.LB = [];
    entries.push(currentEntry);
  }

  return entries;
}

/**
 * 将条目列表转换为 RIS 格式文本
 * @param entries 条目列表
 * @returns RIS 格式文本
 */
export function entriesToRis(entries: RisEntry[]): string {
  const lines: string[] = [];

  for (const entry of entries) {
    for (const [tag, values] of Object.entries(entry)) {
      if (!values || values.length === 0) continue;

      for (const value of values) {
        if (value) {
          lines.push(`${tag}  - ${value}`);
        }
      }
    }
    lines.push('ER  -');
    lines.push('');
  }

  return lines.join('\n');
}

/**
 * 根据标题去重
 * @param entries 条目列表
 * @returns 去重后的条目列表
 */
export function deduplicateEntries(entries: RisEntry[]): RisEntry[] {
  const uniqueMap = new Map<string, RisEntry>();

  for (const entry of entries) {
    if (!entry.TI || entry.TI.length === 0) continue;

    const titleKey = entry.TI[0].toLowerCase().trim();

    if (!uniqueMap.has(titleKey)) {
      uniqueMap.set(titleKey, entry);
    } else {
      // 保留字段更完整的条目
      const existing = uniqueMap.get(titleKey)!;
      if (Object.keys(entry).length > Object.keys(existing).length) {
        uniqueMap.set(titleKey, entry);
      }
    }
  }

  return Array.from(uniqueMap.values());
}

/**
 * 获取条目的期刊名称
 */
export function getJournalName(entry: RisEntry): string | null {
  return entry.T2?.[0] || null;
}

/**
 * 获取条目的标题
 */
export function getTitle(entry: RisEntry): string | null {
  return entry.TI?.[0] || null;
}

/**
 * 统计条目数量
 */
export function countEntries(content: string): number {
  return (content.match(/ER {2}-/g) || []).length;
}

