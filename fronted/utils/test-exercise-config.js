/** 体测项目配置（准备页 / 测试进行页共用） */

export const TEST_INSTRUCTIONS = [
  '请确保光线充足，摄像头对准全身',
  '保持与摄像头距离 1.5~2 米',
  '测试过程中请勿离开画面',
  '请穿着运动服，确保动作标准'
];

export const TEST_FLOW_STEPS = [
  { step: 1, title: '对准全身', desc: '侧面入镜，单人拍摄' },
  { step: 2, title: '开始录制', desc: '按提示完成测试动作' },
  { step: 3, title: 'AI 计数', desc: '系统自动识别动作次数' }
];

export const TEST_EXERCISES = [
  {
    id: 'pull_up',
    label: '引体向上',
    icon: '🏋️',
    apiType: 'pull_up',
    brief: '下颏过杠，双臂伸直'
  },
  {
    id: 'push_up',
    label: '俯卧撑',
    icon: '💪',
    apiType: 'push_up',
    brief: '身体平直，胸部触地'
  },
  {
    id: 'sit_up',
    label: '仰卧起坐',
    icon: '🤸',
    apiType: 'sit_up',
    brief: '双手抱头，起身触膝'
  }
];

export const DEFAULT_EXERCISE_ID = 'pull_up';

export function getExerciseById(id) {
  return TEST_EXERCISES.find((e) => e.id === id) || TEST_EXERCISES[0];
}

/** 兼容旧版 type：pull-up / pull_up */
export function normalizeExerciseId(raw) {
  if (!raw) return DEFAULT_EXERCISE_ID;
  const key = String(raw).trim().toLowerCase().replace(/-/g, '_');
  const map = {
    pull_up: 'pull_up',
    push_up: 'push_up',
    sit_up: 'sit_up'
  };
  return map[key] || DEFAULT_EXERCISE_ID;
}

export function exerciseIdToApiType(id) {
  return getExerciseById(id).apiType;
}
