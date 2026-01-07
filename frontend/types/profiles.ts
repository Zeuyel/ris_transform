/**
 * Profile 相关类型定义（新架构）
 */

export interface CriteriaSet {
  criteria: Record<string, (string | number)[]>;  // 评级系统ID -> 等级列表
}

export interface Profile {
  id: string;
  name: string;
  description: string;
  criteria_sets: Record<string, CriteriaSet>;  // CriteriaSet名称 -> CriteriaSet
}

export interface ProfilesResponse {
  items: Profile[];
}

/**
 * 评级系统信息
 */
export interface RatingSystem {
  id: string;
  name: string;
  levels: (string | number)[];
  // 按类型分组的等级，如 {"期刊": ["A", "B", "C"], "会议": ["A", "B", "C"]}
  // 如果没有类型，则为 {"": ["A", "B", "C"]}
  levels_by_type?: Record<string, (string | number)[]>;
}

export interface RatingSystemsResponse {
  items: RatingSystem[];
}

/**
 * 处理选项（新架构）
 */
export interface ProcessingOptions {
  selectedProfiles: string[];
  deduplicate: boolean;
}

/**
 * API 响应类型
 */
export interface ProcessResponse {
  success: boolean;
  message?: string;
  data?: {
    totalEntries: number;
    outputFiles: string[];
  };
}

