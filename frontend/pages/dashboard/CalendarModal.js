// CalendarModal 组件的业务逻辑
import { ref } from "vue";

export default {
    name: 'CalendarModal',

    emits: ['imageError', 'imageLoad'],

    setup(props, { emit }) {
        const calendarPopup = ref(null);

        const openModal = () => {
            if (calendarPopup.value) {
                calendarPopup.value.open();
            }
        };

        const closeCalendarModal = () => {
            if (calendarPopup.value) {
                calendarPopup.value.close();
            }
        };

        const handleCalendarImageError = () => {
            emit('imageError');
        };

        const handleCalendarImageLoad = () => {
            emit('imageLoad');
        };

        return {
            calendarPopup,
            openModal,
            closeCalendarModal,
            handleCalendarImageError,
            handleCalendarImageLoad
        };
    }
};
