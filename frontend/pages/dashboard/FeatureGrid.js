// FeatureGrid 组件的业务逻辑
export default {
    name: 'FeatureGrid',

    props: {
        features: {
            type: Array,
            required: true,
            default: () => []
        }
    },

    emits: ['navigate'],

    setup(props, { emit }) {
        const handleNavigate = (index) => {
            emit('navigate', index);
        };

        return {
            handleNavigate
        };
    }
};
