// NoticeBar 组件的业务逻辑
export default {
    name: 'NoticeBar',

    props: {
        noticeData: {
            type: Object,
            required: true,
            default: () => ({
                title: "重要通知：请加用户群防走丢！"
            })
        }
    },

    emits: ['click'],

    setup(props, { emit }) {
        const handleClick = () => {
            emit('click');
        };

        return {
            handleClick
        };
    }
};
