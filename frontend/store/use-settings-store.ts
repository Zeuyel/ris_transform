import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * 翻译 API 端点配置
 */
export interface TranslationEndpoint {
  id: string;
  url: string;
  token?: string;
  weight: number;      // 负载均衡权重
  rpm: number;         // requests per minute
  enabled: boolean;
}

/**
 * 翻译服务配置
 */
interface TranslationConfig {
  translateTitle: boolean;
  translateAbstract: boolean;
  endpoints: TranslationEndpoint[];
}

/**
 * 评级系统
 */
interface RatingSystem {
  id: string;
  name: string;
  description?: string;
  enabled: boolean;
}

/**
 * 设置状态接口
 */
interface SettingsState {
  // 翻译配置
  translation: TranslationConfig;

  // 评级系统
  ratingSystems: RatingSystem[];

  // 输出配置
  outputSubfolder: string;

  // UI 配置
  theme: 'light' | 'dark' | 'system';
}

/**
 * 设置操作接口
 */
interface SettingsActions {
  // 翻译配置
  setTranslateTitle: (value: boolean) => void;
  setTranslateAbstract: (value: boolean) => void;
  setTranslationEndpoints: (endpoints: TranslationEndpoint[]) => void;

  // 评级系统
  toggleRatingSystem: (id: string) => void;
  setRatingSystems: (systems: RatingSystem[]) => void;

  // 输出配置
  setOutputSubfolder: (name: string) => void;

  // 主题
  setTheme: (theme: 'light' | 'dark' | 'system') => void;

  // 重置
  resetSettings: () => void;
}

// 便捷别名
type SettingsStore = SettingsState & SettingsActions & {
  translateTitle: boolean;
  translateAbstract: boolean;
  translationEndpoints: TranslationEndpoint[];
};

const DEFAULT_RATING_SYSTEMS: RatingSystem[] = [
  { id: 'CCF', name: 'CCF 推荐', description: '中国计算机学会推荐目录', enabled: true },
  { id: 'FMS', name: 'FMS', description: '金融管理科学推荐期刊', enabled: true },
  { id: 'AJG', name: 'AJG', description: 'Academic Journal Guide', enabled: true },
  { id: 'ZUFE', name: 'ZUFE', description: '浙江财经大学标准', enabled: true },
];

const DEFAULT_TRANSLATION_ENDPOINTS: TranslationEndpoint[] = [
  {
    id: '1',
    url: 'https://deeplx.missuo.ru/translate',
    weight: 1,
    rpm: 60,
    enabled: true,
  },
  {
    id: '2',
    url: 'https://api.deeplx.org/translate',
    weight: 1,
    rpm: 60,
    enabled: true,
  },
];

const initialSettings: SettingsState = {
  translation: {
    translateTitle: false,
    translateAbstract: false,
    endpoints: DEFAULT_TRANSLATION_ENDPOINTS,
  },
  ratingSystems: DEFAULT_RATING_SYSTEMS,
  outputSubfolder: '',
  theme: 'system',
};

/**
 * 设置 Store
 */
export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set, get) => ({
      ...initialSettings,

      // 直接属性（便捷访问）
      translateTitle: initialSettings.translation.translateTitle,
      translateAbstract: initialSettings.translation.translateAbstract,
      translationEndpoints: initialSettings.translation.endpoints,

      setTranslateTitle: (value) => {
        set({
          translation: { ...get().translation, translateTitle: value },
          translateTitle: value,
        });
      },

      setTranslateAbstract: (value) => {
        set({
          translation: { ...get().translation, translateAbstract: value },
          translateAbstract: value,
        });
      },

      setTranslationEndpoints: (endpoints) => {
        set({
          translation: { ...get().translation, endpoints },
          translationEndpoints: endpoints,
        });
      },

      toggleRatingSystem: (id) =>
        set({
          ratingSystems: get().ratingSystems.map((system) =>
            system.id === id ? { ...system, enabled: !system.enabled } : system
          ),
        }),

      setRatingSystems: (systems) => set({ ratingSystems: systems }),

      setOutputSubfolder: (name) => set({ outputSubfolder: name }),

      setTheme: (theme) => set({ theme }),

      resetSettings: () => set({
        ...initialSettings,
        translateTitle: initialSettings.translation.translateTitle,
        translateAbstract: initialSettings.translation.translateAbstract,
        translationEndpoints: initialSettings.translation.endpoints,
      }),
    }),
    {
      name: 'ris-processor-settings',
    }
  )
);