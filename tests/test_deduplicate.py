"""Package name deduplication tests"""
from pipcompilemulti.deduplicate import PackageDeduplicator


def test_package_deduplicator_handles_delimiters_normalization():
    """Tests minor package name variations are handled."""
    package_deduplicator = PackageDeduplicator()
    package_deduplicator.on_discover([
        {'in_path': 'a', 'refs': ['b']},
        {'in_path': 'b', 'refs': []}
    ])
    package_deduplicator.register_packages_for_env('b', {'pkg.name': '1.0'})
    ignored_packages = package_deduplicator.ignored_packages('a')
    assert 'pkg-name' in ignored_packages
    assert 'pkg.name' in ignored_packages
    assert 'pkgname' not in ignored_packages
    assert ignored_packages['Pkg_Name'] == '1.0'
