/**
 * RIS 条目类型定义
 */
export interface RisEntry {
  // 核心字段
  TY?: string[];   // 类型
  TI?: string[];   // 标题
  T2?: string[];   // 期刊名/二级标题
  AU?: string[];   // 作者
  PY?: string[];   // 年份
  AB?: string[];   // 摘要
  DO?: string[];   // DOI
  
  // 扩展字段
  C1?: string[];   // 自定义1 (用于存储翻译后的标题)
  C2?: string[];   // 自定义2 (用于存储翻译后的摘要)
  LB?: string[];   // 标签
  
  // 其他字段 (动态)
  [key: string]: string[] | Record<string, string> | undefined;
}

/**
 * 期刊评级信息
 */
export interface JournalRating {
  system: string;      // 评级系统 (CCF, FMS, AJG, ZUFE)
  level: string;       // 等级
  type?: string;       // 类型 (期刊/会议，用于CCF)
}

/**
 * 处理后的文献条目
 */
export interface ProcessedEntry extends RisEntry {
  ratings: Record<string, string>;  // 各系统评级
  matchedCriteria: string[];        // 匹配的分类标准
}

/**
 * 处理结果
 */
export interface ProcessingResult {
  total: number;
  processed: number;
  outputs: {
    criteria: string;
    count: number;
    entries: ProcessedEntry[];
  }[];
}

