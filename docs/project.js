const utils = require("./utils");

const name = "bocadillo";
const org = "bocadilloproject";
const repo = `${org}/${name}`;
const docs = `https://${org}.github.io`;

module.exports = {
  title: "Bocadillo",
  description: "A modern Python web framework filled with asynchronous salsa",
  name,
  author: "Florimond Manca",
  org,
  orgLink: `https://github.com/${org}`,
  repo,
  docs,
  twitterUser: "bocadillopy",
  algoliaIndex: "bocadilloproject",
  repoPage(path, options = { branch: "master" }) {
    const base = `https://github.com/${repo}/blob/${options.branch}`;
    return utils.maybeRoot(base, path);
  },
  docsPage(path) {
    return utils.maybeRoot(docs, path);
  }
};
