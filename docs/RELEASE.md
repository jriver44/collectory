# Release & Versioning

We follow Semantic Versioning: **MAJOR.MINOR.PATCH**.

To release v1.0.0:

```bash
git checkout main
git pull origin main
git tag v1.0.0
git push origin main --tags
```

Build and upload:

```bash
python -m build
twine upload dist/*
```