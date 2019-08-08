Benefits of using pip-compile-multi
-----------------------------------

I want to summarise, why ``pip-compile-multi`` might be a good addition to your project.
Some of the benefits are achievable with other methods, but I want to be general:

1. Production will not suddenly break after redeployment because of
   backward incompatible dependency release.
2. Every development machine will have the same package versions.
3. Service still uses most recent versions of packages.
   And fresh means best here.
4. Dependencies are upgraded when the time is suitable for the service,
   not whenever they are released.
5. Different environments are separated into different files.
6. ``*.in`` files are small and manageable because they store only direct dependencies.
7. ``*.txt`` files are exhaustive and precise (but you don't need to edit them).
