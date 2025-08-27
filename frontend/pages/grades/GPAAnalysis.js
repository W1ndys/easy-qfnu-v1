export default {
    name: 'GPAAnalysis',
    props: {
        gpaAnalysis: {
            type: Object,
            default: null
        },
        effectiveGpa: {
            type: Object,
            default: null
        },
        totalCourses: {
            type: Number,
            default: 0
        },
        yearlyGpa: {
            type: Object,
            default: null
        },
        semesterGpa: {
            type: Object,
            default: null
        }
    }
}
