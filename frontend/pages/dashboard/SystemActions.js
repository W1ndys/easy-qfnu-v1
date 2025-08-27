// SystemActions 组件的业务逻辑
export default {
    name: 'SystemActions',

    emits: [
        'refresh',
        'logout',
        'userAgreement',
        'clearCache',
        'changelog',
        'contact',
        'feedback',
        'sponsorList',
        'shareSite'
    ],

    setup(props, { emit }) {
        const handleRefresh = () => emit('refresh');
        const handleLogout = () => emit('logout');
        const handleUserAgreement = () => emit('userAgreement');
        const handleClearCache = () => emit('clearCache');
        const handleChangelog = () => emit('changelog');
        const handleContact = () => emit('contact');
        const handleFeedback = () => emit('feedback');
        const handleSponsorList = () => emit('sponsorList');
        const handleShareSite = () => emit('shareSite');

        return {
            handleRefresh,
            handleLogout,
            handleUserAgreement,
            handleClearCache,
            handleChangelog,
            handleContact,
            handleFeedback,
            handleSponsorList,
            handleShareSite
        };
    }
};
