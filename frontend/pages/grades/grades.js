import { ref, computed } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";

// 引入模块化组件
import GPAAnalysis from "./GPAAnalysis.vue";
import CustomToggle from "./CustomToggle.vue";
import CourseList from "./CourseList.vue";
import CustomFooter from "./CustomFooter.vue";
import NoticeModal from "./NoticeModal.vue";

// 引入API服务
import { fetchGradesData, calculateCustomGPA as apiCalculateGPA, groupGradesBySemester, checkLoginStatus } from "./api.js";

export default {
    name: 'Grades',
    components: {
        PageLayout,
        LoadingScreen,
        EmptyState,
        GPAAnalysis,
        CustomToggle,
        CourseList,
        CustomFooter,
        NoticeModal
    },
    setup() {
        // --- 基础页面状态 ---
        const isLoading = ref(true);
        const semesters = ref([]);
        const gpaAnalysis = ref(null);
        const semesterGpa = ref(null);
        const yearlyGpa = ref(null);
        const effectiveGpa = ref(null);
        const totalCourses = ref(0);
        const allCourses = ref([]);

        // --- 自定义GPA计算状态 ---
        const isCustomMode = ref(false);
        const selectedCourses = ref([]); // 存储选中的课程 `index`
        const isCalculating = ref(false);
        const customGPAResult = ref(null); // 用于存储计算结果

        // --- UI交互状态 ---
        const expandedCourses = ref(new Set()); // 存储展开的课程 `index`
        const showNoticeModal = ref(false);

        // --- 计算属性 ---
        const isEmpty = computed(() => semesters.value.length === 0);
        const selectionInfoText = computed(() => `已选 ${selectedCourses.value.length} / ${allCourses.value.length} 门`);
        const isCalculateDisabled = computed(() => isCalculating.value || selectedCourses.value.length === 0);

        // --- 生命周期钩子 ---
        onLoad(() => {
            // 1. 检查登录并获取数据
            checkLoginAndFetch();
            // 2. 延迟500ms后弹出提示窗口
            setTimeout(() => {
                // 可选: 增加判断条件，例如仅在有成绩数据时显示
                if (semesters.value.length > 0 || !isLoading.value) {
                    showNoticeModal.value = true;
                }
            }, 500);
        });

        onShow(() => {
            // 每次页面显示时检查 token，防止在其他页面退出登录后，返回此页面时状态不正确
            if (!uni.getStorageSync("token")) {
                uni.showToast({ title: "请先登录", icon: "none" });
                uni.reLaunch({ url: "/pages/index/index" });
            }
        });

        // --- 数据获取与处理 ---
        const checkLoginAndFetch = () => {
            if (!checkLoginStatus()) return;
            fetchGrades();
        };

        const fetchGrades = async () => {
            isLoading.value = true;
            try {
                const result = await fetchGradesData();
                if (result.success) {
                    allCourses.value = result.data.allCourses;
                    semesters.value = groupGradesBySemester(allCourses.value);
                    gpaAnalysis.value = result.data.gpaAnalysis;
                    semesterGpa.value = result.data.semesterGpa;
                    yearlyGpa.value = result.data.yearlyGpa;
                    effectiveGpa.value = result.data.effectiveGpa;
                    totalCourses.value = allCourses.value.length;
                }
            } finally {
                isLoading.value = false;
            }
        };

        // --- UI交互与辅助函数 ---
        const isCourseSelected = (courseIndex) => selectedCourses.value.includes(courseIndex);
        const isCourseExpanded = (courseIndex) => expandedCourses.value.has(courseIndex);

        const toggleExpand = (courseIndex) => {
            if (expandedCourses.value.has(courseIndex)) {
                expandedCourses.value.delete(courseIndex);
            } else {
                expandedCourses.value.add(courseIndex);
            }
        };

        const handleCourseClick = (course) => {
            if (isCustomMode.value) {
                toggleCourseSelection(course.index);
            } else {
                toggleExpand(course.index);
            }
        };

        const closeNoticeModal = () => {
            showNoticeModal.value = false;
        };

        // --- 自定义GPA计算逻辑 ---
        const toggleCustomMode = (e) => {
            isCustomMode.value = e.detail.value;
            if (!isCustomMode.value) {
                clearSelection();
                clearCustomResult();
            }
        };

        const toggleCourseSelection = (courseIndex) => {
            const idx = selectedCourses.value.indexOf(courseIndex);
            if (idx > -1) {
                selectedCourses.value.splice(idx, 1);
            } else {
                selectedCourses.value.push(courseIndex);
            }
            clearCustomResult(); // 每次选择变化时，清除旧的计算结果
        };

        const selectAllCourses = () => {
            selectedCourses.value = allCourses.value.map(c => c.index);
            clearCustomResult();
        };

        const clearSelection = () => {
            selectedCourses.value = [];
            clearCustomResult();
        };

        const clearCustomResult = () => {
            customGPAResult.value = null;
        };

        const calculateCustomGPA = async () => {
            if (selectedCourses.value.length === 0) {
                uni.showToast({ title: "请至少选择一门课程", icon: "none" });
                return;
            }
            isCalculating.value = true;

            try {
                const result = await apiCalculateGPA(selectedCourses.value);
                if (result.success) {
                    customGPAResult.value = result.data;
                }
            } finally {
                isCalculating.value = false;
            }
        };

        return {
            // 基础状态
            isLoading,
            semesters,
            gpaAnalysis,
            semesterGpa,
            yearlyGpa,
            effectiveGpa,
            totalCourses,
            allCourses,

            // 自定义GPA状态
            isCustomMode,
            selectedCourses,
            isCalculating,
            customGPAResult,

            // UI状态
            expandedCourses,
            showNoticeModal,

            // 计算属性
            isEmpty,
            selectionInfoText,
            isCalculateDisabled,

            // 方法
            fetchGrades,
            handleCourseClick,
            closeNoticeModal,
            toggleCustomMode,
            selectAllCourses,
            clearSelection,
            calculateCustomGPA,
            clearCustomResult
        };
    }
}
