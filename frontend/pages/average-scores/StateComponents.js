export default {
    props: {
        type: {
            type: String,
            required: true,
            validator: (value) => ['empty', 'initial', 'loading'].includes(value)
        },
        message: {
            type: String,
            default: '未找到相关数据'
        }
    },
    emits: ['retry']
};
