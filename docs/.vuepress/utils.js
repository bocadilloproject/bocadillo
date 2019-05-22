const fs = require("fs");

const makeAddDir = dir => file => `/${dir}/${file}`;

function listDir(dir, children) {
  if (!children) {
    // NOTE: children will be sorted in alphabetical order.
    children = fs
      .readdirSync(`docs/${dir}`)
      .filter(file => file.endsWith(".md"))
      .filter(file => file !== "README.md");
  }
  const addDir = makeAddDir(dir);
  return children.map(file => {
    if (typeof file === "string") return addDir(file);
    const [theFile, title] = file;
    return [addDir(theFile), title];
  });
}

function maybeRoot(base, path) {
  return path ? `${base}/${path}` : base;
}

module.exports = { listDir, maybeRoot };
