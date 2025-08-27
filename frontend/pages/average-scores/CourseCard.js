import { formatTime } from './utils.js';

export default {
    props: {
        courseName: {
            type: String,
            required: true
        },
        teachers: {
            type: Object,
            required: true
        }
    },
    setup() {
        return {
            formatTime
        };
    }
};
