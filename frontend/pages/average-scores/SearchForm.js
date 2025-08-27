import { ref, reactive, computed } from "vue";

export default {
    props: {
        loading: {
            type: Boolean,
            default: false
        }
    },
    emits: ['search', 'reset'],
    setup(props, { emit }) {
        // 状态
        const form = reactive({ course: "", teacher: "" });
        const courseError = ref(false);
        const teacherError = ref(false);
        const courseFocused = ref(false);
        const teacherFocused = ref(false);

        // 计算属性
        const courseHint = computed(() => {
            const length = form.course.trim().length;
            if (length === 0) return "请输入课程名称或代码";
            if (length < 3) return `至少需要3个字符，当前${length}个字符`;
            return `已输入${length}个字符`;
        });

        const teacherHint = computed(() => {
            const length = form.teacher.trim().length;
            if (length === 0) return "";
            if (length < 2) return `至少需要2个字符，当前${length}个字符`;
            return `已输入${length}个字符`;
        });

        const canSearch = computed(() => {
            const courseLength = form.course.trim().length;
            const teacherLength = form.teacher.trim().length;
            return courseLength >= 3 && (teacherLength === 0 || teacherLength >= 2);
        });

        // 方法
        function onCourseFocus() {
            courseFocused.value = true;
        }

        function onCourseBlur() {
            courseFocused.value = false;
        }

        function onTeacherFocus() {
            teacherFocused.value = true;
        }

        function onTeacherBlur() {
            teacherFocused.value = false;
        }

        function validateCourse() {
            const length = form.course.trim().length;
            courseError.value = length > 0 && length < 3;
        }

        function validateTeacher() {
            const length = form.teacher.trim().length;
            teacherError.value = length > 0 && length < 2;
        }

        function handleSearch() {
            if (!form.course.trim()) {
                uni.showToast({ title: "请输入课程名称或代码", icon: "none" });
                return;
            }
            if (form.course.trim().length < 3) {
                uni.showToast({ title: "课程名称至少需要3个字符", icon: "none" });
                return;
            }
            if (form.teacher.trim() && form.teacher.trim().length < 2) {
                uni.showToast({ title: "教师姓名至少需要2个字符", icon: "none" });
                return;
            }

            const params = { course: form.course.trim() };
            if (form.teacher.trim()) params.teacher = form.teacher.trim();

            emit('search', params);
        }

        function handleReset() {
            form.course = "";
            form.teacher = "";
            courseError.value = false;
            teacherError.value = false;
            emit('reset');
        }

        return {
            form,
            courseError,
            teacherError,
            courseFocused,
            teacherFocused,
            courseHint,
            teacherHint,
            canSearch,
            onCourseFocus,
            onCourseBlur,
            onTeacherFocus,
            onTeacherBlur,
            validateCourse,
            validateTeacher,
            handleSearch,
            handleReset
        };
    }
};
