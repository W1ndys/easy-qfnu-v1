export default {
    name: 'NoticeModal',
    props: {
        showModal: {
            type: Boolean,
            default: false
        }
    },
    emits: ['close']
}
