use unicode_segmentation::*;
use pyo3::prelude::*;


#[pyfunction]
#[pyo3(signature = (s, extended=true, /))]
fn grapheme_clusters(s: &str, extended: bool) -> PyResult<Vec<&str>> {
    let g = UnicodeSegmentation::graphemes(s, extended).collect::<Vec<&str>>();

    Ok(g)
}

#[pyfunction]
fn unicode_words(s: &str) -> PyResult<Vec<&str>> {
    let g = UnicodeSegmentation::unicode_words(s).collect::<Vec<&str>>();

    Ok(g)
}

#[pyfunction]
fn split_unicode_word_bounds(s: &str) -> PyResult<Vec<&str>> {
    let g = UnicodeSegmentation::split_word_bounds(s).collect::<Vec<&str>>();

    Ok(g)
}

#[pyfunction]
fn unicode_sentences(s: &str) -> PyResult<Vec<&str>> {
    let g = UnicodeSegmentation::unicode_sentences(s).collect::<Vec<&str>>();

    Ok(g)
}

#[pyfunction]
fn split_unicode_sentence_bounds(s: &str) -> PyResult<Vec<&str>> {
    let g = UnicodeSegmentation::split_sentence_bounds(s).collect::<Vec<&str>>();

    Ok(g)
}


#[pymodule]
fn _stringutils(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(grapheme_clusters, m)?)?;
    m.add_function(wrap_pyfunction!(unicode_words, m)?)?;
    m.add_function(wrap_pyfunction!(split_unicode_word_bounds, m)?)?;
    m.add_function(wrap_pyfunction!(unicode_sentences, m)?)?;
    m.add_function(wrap_pyfunction!(split_unicode_sentence_bounds, m)?)?;

    Ok(())
}
