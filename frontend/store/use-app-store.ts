import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Profile } from '@/types/profiles';

/**
 * 处理状态
 */
type ProcessingStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';

/**
 * 处理选项
 */
interface ProcessingOptions {
  selectedProfiles: string[];
  deduplicate: boolean;
}

/**
 * 应用状态接口
 */
interface AppState {
  // 文件状态
  file: File | null;
  fileContent: string | null;

  // Profiles
  profilesList: Profile[];
  selectedProfiles: string[];

  // 处理选项
  options: ProcessingOptions;

  // 处理状态
  status: ProcessingStatus;
  progress: number;
  error: string | null;

  // 结果
  resultBlob: Blob | null;
  resultFilename: string | null;
}

/**
 * 应用操作接口
 */
interface AppActions {
  // 文件操作
  setFile: (file: File | null) => void;
  setFileContent: (content: string | null) => void;

  // Profiles 操作
  setProfilesList: (list: Profile[]) => void;
  toggleProfile: (id: string) => void;
  selectAllProfiles: () => void;
  clearProfiles: () => void;

  // 选项操作
  setOptions: (options: Partial<ProcessingOptions>) => void;

  // 状态操作
  setStatus: (status: ProcessingStatus) => void;
  setProgress: (progress: number) => void;
  setError: (error: string | null) => void;

  // 结果操作
  setResult: (blob: Blob | null, filename: string | null) => void;

  // 重置
  reset: () => void;
}

const initialState: AppState = {
  file: null,
  fileContent: null,
  profilesList: [],
  selectedProfiles: [],
  options: {
    selectedProfiles: [],
    deduplicate: true,
  },
  status: 'idle',
  progress: 0,
  error: null,
  resultBlob: null,
  resultFilename: null,
};

/**
 * 应用状态 Store
 */
export const useAppStore = create<AppState & AppActions>()(
  persist(
    (set, get) => ({
      ...initialState,

      setFile: (file) => set({ file, fileContent: null, status: 'idle', error: null }),

      setFileContent: (content) => set({ fileContent: content }),

      setProfilesList: (list) => set({ profilesList: list }),

      toggleProfile: (id) => {
        const { selectedProfiles } = get();
        const newSelected = selectedProfiles.includes(id)
          ? selectedProfiles.filter((p) => p !== id)
          : [...selectedProfiles, id];
        set({
          selectedProfiles: newSelected,
          options: { ...get().options, selectedProfiles: newSelected }
        });
      },

      selectAllProfiles: () => {
        const { profilesList } = get();
        const allIds = profilesList.map((p) => p.id);
        set({
          selectedProfiles: allIds,
          options: { ...get().options, selectedProfiles: allIds }
        });
      },

      clearProfiles: () => set({
        selectedProfiles: [],
        options: { ...get().options, selectedProfiles: [] }
      }),

      setOptions: (options) => set({
        options: { ...get().options, ...options }
      }),

      setStatus: (status) => set({ status }),

      setProgress: (progress) => set({ progress }),

      setError: (error) => set({ error, status: error ? 'error' : get().status }),

      setResult: (blob, filename) => set({
        resultBlob: blob,
        resultFilename: filename,
        status: blob ? 'completed' : get().status
      }),

      reset: () => set({
        ...initialState,
        profilesList: get().profilesList, // 保留 Profiles 列表
      }),
    }),
    {
      name: 'ris-processor-storage',
      partialize: (state) => ({
        // 只持久化选项配置
        options: state.options,
        selectedProfiles: state.selectedProfiles,
      }),
    }
  )
);

