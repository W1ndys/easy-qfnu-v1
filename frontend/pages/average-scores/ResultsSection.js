import { computed } from "vue";
import CourseCard from './CourseCard.vue';

export default {
    components: {
        CourseCard
    },
    props: {
        resultData: {
            type: Object,
            default: () => ({})
        }
    },
    setup(props) {
        const hasResults = computed(() => Object.keys(props.resultData).length > 0);

        return {
            hasResults
        };
    }
};
