export default {
    name: 'CustomToggle',
    props: {
        isCustomMode: {
            type: Boolean,
            default: false
        }
    },
    emits: ['toggle'],
    setup(props, { emit }) {
        const handleToggle = (e) => {
            emit('toggle', e.detail.value)
        }

        return {
            handleToggle
        }
    }
}
