use numpy::ndarray::Array2;
use numpy::{IntoPyArray, PyArray2};
use pyo3::prelude::*;
use std::cmp::min;
use unicode_segmentation::*;

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
fn split_at_word_boundaries(s: &str) -> PyResult<Vec<&str>> {
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

#[pyfunction]
#[pyo3(signature = (reference, predicted, /))]
fn create_cost_matrix(
    py: Python<'_>,
    reference: Vec<String>,
    predicted: Vec<String>,
) -> PyResult<Bound<'_, PyArray2<u64>>> {
    let n1 = reference.len() + 1;
    let n2 = predicted.len() + 1;
    let mut cost = Array2::zeros((n1, n2));

    for i in 0..n1 {
        cost[[i, 0]] = i as u64;
    }
    for j in 0..n2 {
        cost[[0, j]] = j as u64;
    }

    // Populate the cost matrix
    for i in 0..n1 - 1 {
        for j in 0..n2 - 1 {
            if reference[i] == predicted[j] {
                cost[[i + 1, j + 1]] = cost[[i, j]];
            } else {
                cost[[i + 1, j + 1]] =
                    1 + min(min(cost[[i, j]], cost[[i, j + 1]]), cost[[i + 1, j]]);
            }
        }
    }

    Ok(cost.into_pyarray_bound(py))
}

#[pymodule]
fn _stringutils(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(grapheme_clusters, m)?)?;
    m.add_function(wrap_pyfunction!(unicode_words, m)?)?;
    m.add_function(wrap_pyfunction!(split_at_word_boundaries, m)?)?;
    m.add_function(wrap_pyfunction!(unicode_sentences, m)?)?;
    m.add_function(wrap_pyfunction!(split_unicode_sentence_bounds, m)?)?;
    m.add_function(wrap_pyfunction!(create_cost_matrix, m)?)?;

    Ok(())
}
