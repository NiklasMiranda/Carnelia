const gulp = require('gulp');
const cleanCSS = require('gulp-clean-css');
const uglify = require('gulp-uglify');
const path = require('path');

const baseDir = path.resolve(__dirname, '../..'); // Go up two directories to the project root

gulp.task('minify-css', () => {
    return gulp.src(path.join(baseDir, 'static/css/*.css'))
        .pipe(cleanCSS({ compatibility: 'ie8' }))
        .pipe(gulp.dest(path.join(baseDir, 'static/dist/css')));
});

gulp.task('minify-js', () => {
    return gulp.src(path.join(baseDir, 'static/js/*.js'))
        .pipe(uglify())
        .pipe(gulp.dest(path.join(baseDir, 'static/dist/js')));
});

gulp.task('default', gulp.series('minify-css', 'minify-js'));