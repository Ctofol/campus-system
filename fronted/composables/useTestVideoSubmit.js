/**
 * 体测视频上传、提交与分析轮询（阶段二 session 页接入）
 */
import { ref, onUnmounted } from 'vue';
import { uploadFile, submitActivity, getTestAnalysisStatus } from '@/utils/request.js';
import { exerciseIdToApiType } from '@/utils/test-exercise-config.js';

export function useTestVideoSubmit() {
  const uploadedFile = ref(null);
  const testResult = ref(null);
  const isSubmitting = ref(false);
  const analysisPending = ref(false);
  const taskId = ref(null);
  let pollTimer = null;

  const clearPollTimer = () => {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  };

  onUnmounted(() => {
    clearPollTimer();
  });

  const applyAnalysisResult = (data) => {
    testResult.value = {
      count: data.count ?? 0,
      qualified: !!data.qualified,
      score: data.score,
      score_detail: data.score_detail
    };
  };

  const pollAnalysis = (activityId) => {
    clearPollTimer();
    analysisPending.value = true;
    testResult.value = null;
    let tries = 0;
    const maxTries = 40;
    pollTimer = setInterval(async () => {
      tries += 1;
      try {
        const st = await getTestAnalysisStatus(activityId);
        if (st.analysis_status === 'success') {
          clearPollTimer();
          analysisPending.value = false;
          applyAnalysisResult(st);
          uni.showToast({ title: '分析完成', icon: 'success' });
        } else if (st.analysis_status === 'failed') {
          clearPollTimer();
          analysisPending.value = false;
          uni.showToast({
            title: st.analysis_error || '分析失败',
            icon: 'none'
          });
        } else if (tries >= maxTries) {
          clearPollTimer();
          analysisPending.value = false;
          uni.showToast({ title: '分析超时，请稍后在记录中查看', icon: 'none' });
        }
      } catch (e) {
        if (tries >= maxTries) {
          clearPollTimer();
          analysisPending.value = false;
        }
      }
    }, 2000);
  };

  const validateAndUpload = async (filePath, fileType) => {
    try {
      const fileInfo = await new Promise((resolve, reject) => {
        uni.getFileInfo({
          filePath,
          success: resolve,
          fail: reject
        });
      });

      const maxSize = fileType === 'video' ? 100 * 1024 * 1024 : 5 * 1024 * 1024;
      if (fileInfo.size > maxSize) {
        uni.showToast({
          title: `文件大小超过限制（${fileType === 'video' ? '100MB' : '5MB'}）`,
          icon: 'none'
        });
        return;
      }

      uni.showLoading({ title: '上传中...' });
      const uploadResult = await uploadFile(filePath, fileType);

      uploadedFile.value = {
        url: uploadResult.url,
        type: fileType,
        size: uploadResult.size,
        originalName: uploadResult.original_filename
      };

      uni.hideLoading();
      uni.showToast({ title: '上传成功', icon: 'success' });
    } catch (error) {
      uni.hideLoading();
      console.error('Upload error:', error);
      uni.showToast({ title: '上传失败，请重试', icon: 'none' });
    }
  };

  const chooseVideoFromGallery = () => {
    // #ifdef MP-WEIXIN
    uni.chooseMedia({
      count: 1,
      mediaType: ['video'],
      sourceType: ['album'],
      maxDuration: 300,
      success: (res) => {
        const media = res.tempFiles[0];
        validateAndUpload(media.tempFilePath, 'video');
      },
      fail: () => {
        uni.showToast({ title: '选择视频失败', icon: 'none' });
      }
    });
    // #endif
    // #ifndef MP-WEIXIN
    uni.chooseVideo({
      sourceType: ['album'],
      maxDuration: 300,
      success: (res) => {
        validateAndUpload(res.tempFilePath, 'video');
      },
      fail: () => {
        uni.showToast({ title: '选择视频失败', icon: 'none' });
      }
    });
    // #endif
  };

  const recordVideo = () => {
    // #ifdef MP-WEIXIN
    uni.chooseMedia({
      count: 1,
      mediaType: ['video'],
      sourceType: ['camera'],
      maxDuration: 300,
      success: (res) => {
        const media = res.tempFiles[0];
        validateAndUpload(media.tempFilePath, 'video');
      },
      fail: () => {
        uni.showToast({ title: '拍摄视频失败', icon: 'none' });
      }
    });
    // #endif
    // #ifndef MP-WEIXIN
    uni.chooseVideo({
      sourceType: ['camera'],
      maxDuration: 300,
      success: (res) => {
        validateAndUpload(res.tempFilePath, 'video');
      },
      fail: () => {
        uni.showToast({ title: '拍摄视频失败', icon: 'none' });
      }
    });
    // #endif
  };

  const showUploadOptions = () => {
    uni.showActionSheet({
      itemList: ['从相册选择视频', '拍摄视频'],
      success: (res) => {
        if (res.tapIndex === 0) chooseVideoFromGallery();
        else if (res.tapIndex === 1) recordVideo();
      }
    });
  };

  const submitTest = async (exerciseId) => {
    if (!uploadedFile.value) {
      uni.showToast({ title: '请先上传视频', icon: 'none' });
      return null;
    }

    isSubmitting.value = true;

    const activityData = {
      type: 'test',
      source: taskId.value ? 'task' : 'free',
      task_id: taskId.value || undefined,
      started_at: new Date().toISOString(),
      ended_at: new Date().toISOString(),
      metrics: {
        duration: 0,
        video_url: uploadedFile.value.url,
        qualified: false,
        count: 0,
        exercise_type: exerciseIdToApiType(exerciseId)
      },
      evidence: []
    };

    try {
      uni.showLoading({ title: '提交中...' });
      const result = await submitActivity(activityData);
      uni.hideLoading();

      const status = result.metrics?.analysis_status;
      if (status === 'pending' && result.id) {
        uni.showToast({ title: '已提交，正在分析', icon: 'none' });
        pollAnalysis(result.id);
      } else if (result.metrics) {
        applyAnalysisResult(result.metrics);
        uni.showToast({ title: '提交成功', icon: 'success' });
      }
      return result;
    } catch (error) {
      uni.hideLoading();
      console.error('Submit error:', error);
      const errorMsg = error.message || error.detail || '提交失败，请重试';
      uni.showToast({ title: errorMsg, icon: 'none' });
      return null;
    } finally {
      isSubmitting.value = false;
    }
  };

  const resetUpload = () => {
    uploadedFile.value = null;
    testResult.value = null;
    analysisPending.value = false;
    clearPollTimer();
  };

  return {
    uploadedFile,
    testResult,
    isSubmitting,
    analysisPending,
    taskId,
    showUploadOptions,
    validateAndUpload,
    submitTest,
    resetUpload,
    clearPollTimer
  };
}
