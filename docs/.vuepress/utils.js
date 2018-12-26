const fs = require('fs');

function listDir(dir, children) {
    if (children === undefined) {
        // NOTE: children will be sorted in alphabetical order.
        children = fs.readdirSync(`docs/${dir}`)
            .filter(file => file.endsWith('.md'))
            .filter(file => file !== 'README.md');
    }
    return children.map(file => `/${dir}/${file}`);
}

module.exports = {listDir};
