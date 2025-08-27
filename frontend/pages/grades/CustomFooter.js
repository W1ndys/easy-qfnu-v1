import { computed } from 'vue'

export default {
    name: 'CustomFooter',
    props: {
        isCustomMode: {
            type: Boolean,
            default: false
        },
        customGPAResult: {
            type: Object,
            default: null
        },
        selectedCourses: {
            type: Array,
            default: () => []
        },
        allCourses: {
            type: Array,
            default: () => []
        },
        isCalculating: {
            type: Boolean,
            default: false
        }
    },
    emits: ['clearResult', 'selectAll', 'clearSelection', 'calculate'],
    setup(props, { emit }) {
        const selectionInfoText = computed(() => `已选 ${props.selectedCourses.length} / ${props.allCourses.length} 门`)
        const isCalculateDisabled = computed(() => props.isCalculating || props.selectedCourses.length === 0)

        return {
            selectionInfoText,
            isCalculateDisabled
        }
    }
}
