// ProfileCard 组件的业务逻辑
export default {
    name: 'ProfileCard',

    props: {
        profile: {
            type: Object,
            required: true,
            default: () => ({
                student_name: "W1ndys",
                student_id: "加载中...",
                college: "曲奇学院",
                major: "曲奇专业",
                class_name: "22曲奇班",
            })
        }
    },

    setup(props) {
        // 这里可以添加组件的业务逻辑
        // 目前 ProfileCard 主要是展示组件，逻辑较少

        return {
            // 暴露给模板的数据和方法
        };
    }
};
