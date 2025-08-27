// SupportCard 组件的业务逻辑
export default {
    name: 'SupportCard',

    emits: ['imageError', 'imageLoad'],

    setup(props, { emit }) {
        const handleImageError = () => {
            emit('imageError');
        };

        const handleImageLoad = () => {
            emit('imageLoad');
        };

        return {
            handleImageError,
            handleImageLoad
        };
    }
};
