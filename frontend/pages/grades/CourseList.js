export default {
    name: 'CourseList',
    props: {
        semesters: {
            type: Array,
            default: () => []
        },
        isCustomMode: {
            type: Boolean,
            default: false
        },
        selectedCourses: {
            type: Array,
            default: () => []
        },
        expandedCourses: {
            type: Set,
            default: () => new Set()
        }
    },
    emits: ['courseClick'],
    setup(props, { emit }) {
        const isCourseSelected = (courseIndex) => props.selectedCourses.includes(courseIndex)
        const isCourseExpanded = (courseIndex) => props.expandedCourses.has(courseIndex)

        const getScoreClass = (score) => {
            const numScore = parseFloat(score)
            if (isNaN(numScore)) return 'score-text-grade' // 用于"优秀"、"良好"等文本成绩
            if (numScore >= 90) return 'score-high'
            if (numScore >= 75) return 'score-mid'
            if (numScore >= 60) return 'score-low'
            return 'score-fail'
        }

        return {
            isCourseSelected,
            isCourseExpanded,
            getScoreClass
        }
    }
}
