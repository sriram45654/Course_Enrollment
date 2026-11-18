/**
 * Student Course Enrollment System
 * Discrete Mathematics (3rd Sem CSE)
 * JavaScript Entry Script
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Student Course Enrollment System loaded.');
    checkBackendStatus();
    initVennVisualizer();
    initRelationMatrixFilter();
    initSymmetricDifferenceCalculator();
    initSetOperationsValidation();
});

/**
 * Checks system health & backend connectivity
 */
async function checkBackendStatus() {
    const statusPill = document.getElementById('db-status-pill');
    const statusText = document.getElementById('db-status-text');

    try {
        const response = await fetch('/api/status');
        if (!response.ok) {
            throw new Error(`HTTP Error status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Backend Status Response:', data);

        if (data.status === 'Online' || data.database_connected) {
            statusPill.classList.add('online');
            statusPill.classList.remove('offline');
            if (data.database_connected) {
                statusText.textContent = 'System & MySQL Connected';
            } else {
                statusText.textContent = 'Flask Online (MySQL Disconnected)';
            }
        }
    } catch (error) {
        console.warn('Backend API fetch error:', error);
        statusPill.classList.add('offline');
        statusPill.classList.remove('online');
        statusText.textContent = 'Backend Offline';
    }
}

/**
 * Course Enrollment Venn Visualizer Module
 */
let vennState = {
    courseA: 'C01',
    courseB: 'C02',
    op: 'union',
    data: null
};

function initVennVisualizer() {
    const selectA = document.getElementById('venn_course_a');
    const selectB = document.getElementById('venn_course_b');
    const opBtns = document.querySelectorAll('.venn-op-btn');
    const regionCards = document.querySelectorAll('.venn-region-card');
    const regionPaths = document.querySelectorAll('.venn-path');

    if (!selectA || !selectB) return;

    vennState.courseA = selectA.value || 'C01';
    vennState.courseB = selectB.value || 'C02';

    // Dropdown change listeners
    selectA.addEventListener('change', (e) => {
        if (selectA.value === selectB.value) {
            // Find another option for selectB
            for (let opt of selectB.options) {
                if (opt.value !== selectA.value) {
                    selectB.value = opt.value;
                    vennState.courseB = opt.value;
                    break;
                }
            }
        }
        vennState.courseA = e.target.value;
        fetchAndRenderVenn();
    });

    selectB.addEventListener('change', (e) => {
        if (selectB.value === selectA.value) {
            // Find another option for selectA
            for (let opt of selectA.options) {
                if (opt.value !== selectB.value) {
                    selectA.value = opt.value;
                    vennState.courseA = opt.value;
                    break;
                }
            }
        }
        vennState.courseB = e.target.value;
        fetchAndRenderVenn();
    });

    // Operation button click listeners
    opBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            opBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            vennState.op = btn.getAttribute('data-op');
            renderVennHighlightsAndResults();
        });
    });

    // Interactive clicking on region cards or SVG paths
    regionCards.forEach(card => {
        card.addEventListener('click', () => {
            const targetOp = card.getAttribute('data-region');
            if (targetOp) {
                selectVennOperation(targetOp);
            }
        });
    });

    regionPaths.forEach(path => {
        path.addEventListener('click', () => {
            if (path.classList.contains('region-left')) {
                selectVennOperation('diff_a_b');
            } else if (path.classList.contains('region-intersect')) {
                selectVennOperation('intersection');
            } else if (path.classList.contains('region-right')) {
                selectVennOperation('diff_b_a');
            }
        });
    });

    // Initial fetch
    fetchAndRenderVenn();
}

function selectVennOperation(opName) {
    const opBtn = document.querySelector(`.venn-op-btn[data-op="${opName}"]`);
    if (opBtn) {
        opBtn.click();
    }
}

async function fetchAndRenderVenn() {
    try {
        const response = await fetch(`/api/venn-data?course_a=${vennState.courseA}&course_b=${vennState.courseB}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch Venn data: ${response.status}`);
        }
        const data = await response.json();
        vennState.data = data;

        // Update region content
        updateVennRegionContent(data);
        // Update highlights and result table
        renderVennHighlightsAndResults();
    } catch (error) {
        console.error('Error fetching Venn data:', error);
    }
}

function updateVennRegionContent(data) {
    const titleA = document.getElementById('svg-title-a');
    const titleB = document.getElementById('svg-title-b');
    
    if (titleA && data.course_a) {
        titleA.textContent = `${data.course_a.course_name} (${data.course_a.course_id})`;
    }
    if (titleB && data.course_b) {
        titleB.textContent = `${data.course_b.course_name} (${data.course_b.course_id})`;
    }

    // Header pills
    const pillLeft = document.getElementById('pill-left-name');
    const pillIntersect = document.getElementById('pill-intersect-name');
    const pillRight = document.getElementById('pill-right-name');

    if (pillLeft) pillLeft.textContent = `${data.course_a.course_id} Only`;
    if (pillIntersect) pillIntersect.textContent = `${data.course_a.course_id} ∩ ${data.course_b.course_id}`;
    if (pillRight) pillRight.textContent = `${data.course_b.course_id} Only`;

    // Counts on cards
    const countLeft = document.getElementById('count-left');
    const countIntersect = document.getElementById('count-intersect');
    const countRight = document.getElementById('count-right');

    if (countLeft) countLeft.textContent = data.counts.left_only;
    if (countIntersect) countIntersect.textContent = data.counts.intersection;
    if (countRight) countRight.textContent = data.counts.right_only;

    // Counts inside SVG diagram circles
    const svgCountLeft = document.getElementById('svg-count-left');
    const svgCountIntersect = document.getElementById('svg-count-intersect');
    const svgCountRight = document.getElementById('svg-count-right');

    if (svgCountLeft) svgCountLeft.textContent = data.counts.left_only;
    if (svgCountIntersect) svgCountIntersect.textContent = data.counts.intersection;
    if (svgCountRight) svgCountRight.textContent = data.counts.right_only;

    // Student scroll lists
    renderStudentListScroll('scroll-left', data.left_only, 'No students enrolled only in ' + data.course_a.course_id);
    renderStudentListScroll('scroll-intersect', data.intersection, 'No common enrolled students');
    renderStudentListScroll('scroll-right', data.right_only, 'No students enrolled only in ' + data.course_b.course_id);
}

function renderStudentListScroll(elementId, studentList, emptyText) {
    const container = document.getElementById(elementId);
    if (!container) return;

    if (!studentList || studentList.length === 0) {
        container.innerHTML = `<div class="region-empty">${emptyText}</div>`;
        return;
    }

    let html = '';
    studentList.forEach(s => {
        html += `
            <div class="student-chip" title="${s.student_id} - ${s.name}">
                <span class="chip-id">${s.student_id}</span>
                <span class="chip-name">${s.name}</span>
            </div>
        `;
    });
    container.innerHTML = html;
}

function renderVennHighlightsAndResults() {
    const data = vennState.data;
    if (!data) return;

    const pathLeft = document.getElementById('path-left');
    const pathIntersect = document.getElementById('path-intersect');
    const pathRight = document.getElementById('path-right');

    const cardLeft = document.getElementById('card-region-left');
    const cardIntersect = document.getElementById('card-region-intersect');
    const cardRight = document.getElementById('card-region-right');

    // Reset all active classes
    [pathLeft, pathIntersect, pathRight, cardLeft, cardIntersect, cardRight].forEach(el => {
        if (el) el.classList.remove('active');
    });

    let resultList = [];
    let notationStr = '';
    let descStr = '';
    let proofFormat = '';

    const cA = data.course_a.course_id;
    const cB = data.course_b.course_id;
    const nameA = data.course_a.course_name;
    const nameB = data.course_b.course_name;

    switch (vennState.op) {
        case 'union':
            if (pathLeft) pathLeft.classList.add('active');
            if (pathIntersect) pathIntersect.classList.add('active');
            if (pathRight) pathRight.classList.add('active');

            if (cardLeft) cardLeft.classList.add('active');
            if (cardIntersect) cardIntersect.classList.add('active');
            if (cardRight) cardRight.classList.add('active');

            resultList = data.union;
            notationStr = `${cA} ∪ ${cB}`;
            descStr = `Students enrolled in ${nameA} OR ${nameB} (Set Union A ∪ B)`;
            proofFormat = `s ∈ (${cA} ∪ ${cB})`;
            break;

        case 'intersection':
            if (pathIntersect) pathIntersect.classList.add('active');
            if (cardIntersect) cardIntersect.classList.add('active');

            resultList = data.intersection;
            notationStr = `${cA} ∩ ${cB}`;
            descStr = `Students enrolled in BOTH ${nameA} AND ${nameB} (Set Intersection A ∩ B)`;
            proofFormat = `s ∈ ${cA} ∧ s ∈ ${cB}`;
            break;

        case 'diff_a_b':
            if (pathLeft) pathLeft.classList.add('active');
            if (cardLeft) cardLeft.classList.add('active');

            resultList = data.left_only;
            notationStr = `${cA} − ${cB}`;
            descStr = `Students enrolled in ${nameA} BUT NOT ${nameB} (Set Difference A − B)`;
            proofFormat = `s ∈ ${cA} ∧ s ∉ ${cB}`;
            break;

        case 'diff_b_a':
            if (pathRight) pathRight.classList.add('active');
            if (cardRight) cardRight.classList.add('active');

            resultList = data.right_only;
            notationStr = `${cB} − ${cA}`;
            descStr = `Students enrolled in ${nameB} BUT NOT ${nameA} (Set Difference B − A)`;
            proofFormat = `s ∈ ${cB} ∧ s ∉ ${cA}`;
            break;

        case 'symmetric_difference':
            if (pathLeft) pathLeft.classList.add('active');
            if (pathRight) pathRight.classList.add('active');
            if (cardLeft) cardLeft.classList.add('active');
            if (cardRight) cardRight.classList.add('active');

            // Combine students enrolled in only A or only B
            resultList = [...(data.left_only || []), ...(data.right_only || [])].sort((a, b) => a.student_id.localeCompare(b.student_id));
            notationStr = `${cA} △ ${cB}`;
            descStr = `Students enrolled in ${nameA} OR ${nameB} but NOT BOTH (Symmetric Difference A △ B = (A − B) ∪ (B − A))`;
            proofFormat = `(s ∈ ${cA} ∧ s ∉ ${cB}) ∨ (s ∈ ${cB} ∧ s ∉ ${cA})`;
            break;
    }

    // Update Result Bar
    const notationEl = document.getElementById('venn-op-notation');
    const descEl = document.getElementById('venn-op-description');
    const countEl = document.getElementById('venn-op-count');

    if (notationEl) notationEl.textContent = notationStr;
    if (descEl) descEl.textContent = descStr;
    if (countEl) countEl.textContent = `${resultList.length} Student(s) Result`;

    // Render Result Table Body
    const tbody = document.getElementById('venn-result-list');
    if (!tbody) return;

    if (resultList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-state">
                    <p>No students found for Set Operation: <strong>${notationStr}</strong></p>
                </td>
            </tr>
        `;
    } else {
        let rowsHtml = '';
        resultList.forEach((s, index) => {
            rowsHtml += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="id-tag">${s.student_id}</span></td>
                    <td class="font-medium">${s.name}</td>
                    <td><span class="membership-badge">${proofFormat}</span></td>
                </tr>
            `;
        });
        tbody.innerHTML = rowsHtml;
    }
}

/**
 * Relation Matrix Live Search Filter
 */
function initRelationMatrixFilter() {
    const searchInput = document.getElementById('matrixSearchInput');
    const table = document.getElementById('relationMatrixTable');
    if (!searchInput || !table) return;

    const rows = table.querySelectorAll('tbody tr.matrix-row');

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim().toLowerCase();
        let visibleCount = 0;

        rows.forEach(row => {
            const studentId = (row.getAttribute('data-id') || '').toLowerCase();
            const studentName = (row.getAttribute('data-name') || '').toLowerCase();

            if (!query || studentId.includes(query) || studentName.includes(query)) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
    });
}

/**
 * Course Set Operations Validation (Form validation preventing same course)
 */
function initSetOperationsValidation() {
    const form = document.getElementById('setOpsForm');
    const courseA = document.getElementById('course_a');
    const courseB = document.getElementById('course_b');
    const errorAlert = document.getElementById('set-ops-client-error');

    if (!form || !courseA || !courseB) return;

    function checkDistinctCourses() {
        if (courseA.value && courseB.value && courseA.value === courseB.value) {
            if (errorAlert) errorAlert.style.display = 'flex';
            return false;
        } else {
            if (errorAlert) errorAlert.style.display = 'none';
            return true;
        }
    }

    courseA.addEventListener('change', () => {
        if (courseA.value && courseB.value && courseA.value === courseB.value) {
            // Find another option for courseB
            for (let opt of courseB.options) {
                if (opt.value && opt.value !== courseA.value) {
                    courseB.value = opt.value;
                    break;
                }
            }
        }
        checkDistinctCourses();
    });

    courseB.addEventListener('change', () => {
        if (courseA.value && courseB.value && courseA.value === courseB.value) {
            // Find another option for courseA
            for (let opt of courseA.options) {
                if (opt.value && opt.value !== courseB.value) {
                    courseA.value = opt.value;
                    break;
                }
            }
        }
        checkDistinctCourses();
    });

    form.addEventListener('submit', (e) => {
        if (!checkDistinctCourses()) {
            e.preventDefault();
            alert('Please select two distinct courses. Course A and Course B cannot be the same.');
        }
    });
}

/**
 * Dedicated Interactive Symmetric Difference Calculator Module
 */
function initSymmetricDifferenceCalculator() {
    const selectA = document.getElementById('sym_diff_course_a');
    const selectB = document.getElementById('sym_diff_course_b');
    const btnCompute = document.getElementById('btn-compute-sym-diff');
    const alertBox = document.getElementById('sym-diff-alert');
    const alertMsg = document.getElementById('sym-diff-alert-msg');
    const loadingText = document.getElementById('sym-diff-loading');

    if (!selectA || !selectB || !btnCompute) return;

    // Ensure distinct selection on change
    selectA.addEventListener('change', () => {
        if (selectA.value === selectB.value) {
            for (let opt of selectB.options) {
                if (opt.value !== selectA.value) {
                    selectB.value = opt.value;
                    break;
                }
            }
        }
        if (alertBox) alertBox.style.display = 'none';
    });

    selectB.addEventListener('change', () => {
        if (selectB.value === selectA.value) {
            for (let opt of selectA.options) {
                if (opt.value !== selectB.value) {
                    selectA.value = opt.value;
                    break;
                }
            }
        }
        if (alertBox) alertBox.style.display = 'none';
    });

    btnCompute.addEventListener('click', () => {
        executeSymmetricDifferenceCalculation();
    });

    async function executeSymmetricDifferenceCalculation() {
        const cA = selectA.value;
        const cB = selectB.value;

        if (cA === cB) {
            if (alertBox && alertMsg) {
                alertMsg.textContent = 'Please choose two different courses. Symmetric Difference on identical sets yields an empty set: A △ A = ∅.';
                alertBox.style.display = 'flex';
            }
            return;
        }

        if (alertBox) alertBox.style.display = 'none';
        if (loadingText) loadingText.style.display = 'inline-flex';
        btnCompute.disabled = true;

        try {
            const response = await fetch(`/api/symmetric-difference?course_a=${cA}&course_b=${cB}`);
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || `HTTP error ${response.status}`);
            }

            const data = await response.json();
            renderSymmetricDifferenceResults(data);
        } catch (error) {
            console.error('Error fetching symmetric difference:', error);
            if (alertBox && alertMsg) {
                alertMsg.textContent = error.message || 'Error computing symmetric difference.';
                alertBox.style.display = 'flex';
            }
        } finally {
            if (loadingText) loadingText.style.display = 'none';
            btnCompute.disabled = false;
        }
    }

    function renderSymmetricDifferenceResults(data) {
        const notationEl = document.getElementById('sym-diff-res-notation');
        const explEl = document.getElementById('sym-diff-res-explanation');
        const pillOnlyA = document.getElementById('sym-pill-only-a');
        const pillOnlyB = document.getElementById('sym-pill-only-b');
        const pillExcluded = document.getElementById('sym-pill-excluded');
        const pillTotal = document.getElementById('sym-pill-total');
        const tbody = document.getElementById('sym-diff-table-body');

        const cA = data.course_a.course_id;
        const cB = data.course_b.course_id;
        const nameA = data.course_a.course_name;
        const nameB = data.course_b.course_name;

        if (notationEl) notationEl.textContent = `${cA} △ ${cB}`;
        if (explEl) {
            explEl.innerHTML = `Students enrolled in <strong>${nameA}</strong> OR <strong>${nameB}</strong>, but strictly NOT in both. <code>${cA} △ ${cB} = (${cA} − ${cB}) ∪ (${cB} − ${cA})</code>`;
        }

        if (pillOnlyA) pillOnlyA.textContent = `${cA} Only: ${data.counts.only_a}`;
        if (pillOnlyB) pillOnlyB.textContent = `${cB} Only: ${data.counts.only_b}`;
        if (pillExcluded) pillExcluded.textContent = `Both Excluded (${cA} ∩ ${cB}): ${data.counts.both_excluded}`;
        if (pillTotal) pillTotal.textContent = `Total |A △ B| = ${data.counts.total_symmetric_diff} Student(s)`;

        if (!tbody) return;

        const students = data.symmetric_difference || [];
        if (students.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="empty-state">
                        <span class="empty-icon">∅</span>
                        <p><strong>${cA} △ ${cB} = ∅ (Empty Result Set)</strong></p>
                        <p>No students qualify for Symmetric Difference between ${nameA} and ${nameB}.
                        ${data.counts.both_excluded > 0 ? `(All ${data.counts.both_excluded} enrolled student(s) are taking BOTH courses and are therefore excluded).` : '(Neither course has enrolled students).'}</p>
                    </td>
                </tr>
            `;
        } else {
            let html = '';
            students.forEach((s, idx) => {
                html += `
                    <tr>
                        <td>${idx + 1}</td>
                        <td><span class="id-tag">${s.student_id}</span></td>
                        <td class="font-medium">${s.name}</td>
                        <td><span class="course-tag">${s.enrolled_in}</span></td>
                        <td><span class="membership-badge">${s.membership}</span></td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        }
    }

    // Run initial calculation once on page load
    executeSymmetricDifferenceCalculation();
}

/**
 * Utility functions for Discrete Math Set Theory operations
 */
const SetTheoryUtils = {
    union: (setA, setB) => new Set([...setA, ...setB]),
    intersection: (setA, setB) => new Set([...setA].filter(x => setB.has(x))),
    difference: (setA, setB) => new Set([...setA].filter(x => !setB.has(x))),
    symmetricDifference: (setA, setB) => {
        const diffA = new Set([...setA].filter(x => !setB.has(x)));
        const diffB = new Set([...setB].filter(x => !setA.has(x)));
        return new Set([...diffA, ...diffB]);
    },
    cartesianProduct: (setA, setB) => {
        const product = [];
        for (const a of setA) {
            for (const b of setB) {
                product.push([a, b]);
            }
        }
        return product;
    }
};

window.SetTheoryUtils = SetTheoryUtils;
