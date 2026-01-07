/**
 * 评级系统枚举
 */
export type RatingSystem = 'CCF' | 'FMS' | 'AJG' | 'ZUFE' | string;

/**
 * 评级系统配置
 */
export interface RatingSystemConfig {
  id: string;
  name: string;
  description: string;
}

/**
 * 评级文件映射配置
 */
export interface RatingFileMapping {
  paper_name: string;  // JSON 中期刊名称字段
  level: string;       // JSON 中等级字段
  type?: string;       // JSON 中类型字段 (可选)
}

/**
 * 分类标准
 * key: 评级系统ID
 * value: 符合条件的等级列表
 */
export interface SelectionCriteria {
  [systemId: string]: (string | number)[];
}

/**
 * 分类标准项
 */
export interface CriteriaItem {
  id: string;
  name: string;
  description: string;
  criteria: SelectionCriteria;
}

/**
 * 组合标准 (Profile)
 * 多个分类标准的组合
 */
export interface SelectionProfile {
  [setName: string]: SelectionCriteria;
}

/**
 * 全局配置
 */
export interface AppConfig {
  ratingSystems: Record<string, RatingSystemConfig>;
  ratingFilePaths: Record<string, string>;
  jsonAttributeMapping: Record<string, RatingFileMapping>;
  translationTokens: {
    missuo?: string;
    linuxdo?: string;
  };
}

/**
 * 处理选项
 */
export interface ProcessingOptions {
  selectedCriteria: string[];
  includeProfiles: boolean;
  deduplicate: boolean;
  translateTitle: boolean;
  translateAbstract: boolean;
}

/**
 * API 响应类型
 */
export interface CriteriaResponse {
  items: CriteriaItem[];
}

export interface ProcessResponse {
  success: boolean;
  message?: string;
  data?: {
    totalEntries: number;
    outputFiles: string[];
  };
}

