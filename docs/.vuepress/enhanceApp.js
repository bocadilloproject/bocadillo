export default ({ router }) => {
    router.addRoutes([
        // After renaming "Topics" section to "Guides"
        { path: '/topics/', redirect: '/guides/' },
    ])
}
