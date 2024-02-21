
var quill = new Quill('#editor', {
    modules: {
      toolbar: '#toolbar', 
    },
    theme: 'snow'
  });
  
 const comment = document.getElementById('comment');
 const commentsection = document.getElementById('comment-section');
 const commentexit = document.getElementById('comment-exit');

 comment.addEventListener('click', function() {
    if (commentsection.style.display === 'none') {
        commentsection.style.display = 'block'; 
    } else {
        commentsection.style.display = 'none'; 
    }
  });

commentexit.addEventListener('click', function(){
    commentsection.style.display = 'none';
})


function getSelectedText() {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        return selection.toString();
    }
    return null;
}

function saveComment(selectedText, commentInput) {
    const comments = JSON.parse(localStorage.getItem('comments')) || [];
    comments.push({ text: selectedText, comment: commentInput });
    localStorage.setItem('comments', JSON.stringify(comments));
}

function deleteComment(index) {
    const comments = JSON.parse(localStorage.getItem('comments')) || [];
    comments.splice(index, 1);
    localStorage.setItem('comments', JSON.stringify(comments));
    loadComments();
}

function editComment(index, newText) {
    const comments = JSON.parse(localStorage.getItem('comments')) || [];
    comments[index].comment = newText;
    localStorage.setItem('comments', JSON.stringify(comments));
    loadComments(); 
}


function loadComments() {
    const comments = JSON.parse(localStorage.getItem('comments')) || [];
    const commentsContainer = document.querySelector('#comments');
    commentsContainer.innerHTML = '';

    comments.forEach((comment, index) => {
        const commentElement = document.createElement('div');
        commentElement.classList.add('comments-here')
        commentElement.innerHTML = `
            <strong>Comment on "${comment.text}":</strong>
            <span id="commentText_${index}">${comment.comment}</span>
            <button class="edit-comment" onclick="editCommentPrompt(${index})"><i class='bx bx-edit'></i></button>
            <button class="delete-comment" onclick="deleteComment(${index})"><i class='bx bx-trash'></i></button>`;
        commentElement.addEventListener('mouseover', function () {
            if (!commentElement.classList.contains('highlighted')) {
                highlightText(comment.text);
            }
        });
        commentElement.addEventListener('mouseout', function () {
            removeHighlight();
        });
        commentsContainer.appendChild(commentElement);
    });
}

function editCommentPrompt(index) {
    const newText = prompt("Edit your comment:", "");
    if (newText !== null) {
        editComment(index, newText);
    }
}

function addComment() {
    const commentInput = document.querySelector('#commentInput').value;
    const selectedText = getSelectedText();

    if (!selectedText) {
        alert("Please select a word or phrase to comment on.");
        return;
    }

    saveComment(selectedText, commentInput);

    const commentElement = document.createElement('div');
    const commentId = `comment-${Date.now()}`;
    commentElement.id = commentId;
    commentElement.dataset.highlightedText = selectedText;
    commentElement.innerHTML = `<strong>Comment on "${selectedText}":</strong> ${commentInput}`;

    document.querySelector('#comments').appendChild(commentElement);

    const range = window.getSelection().getRangeAt(0);
    const span = document.createElement('span');
    span.className = 'highlighted';
    range.surroundContents(span);


    highlightSelectedText(selectedText);

    document.querySelector('#commentInput').value = '';

    loadComments();
}

function highlightText(text) {
    const editorContent = document.getElementById('editor');
    const editorText = editorContent.innerHTML;
    const highlightedText = `<span class="highlighted">${text}</span>`;
    const newEditorText = editorText.replace(new RegExp(text, 'g'), highlightedText);
    editorContent.innerHTML = newEditorText;
}

document.querySelector('#comments').addEventListener('mouseover', function (event) {
    const commentElement = event.target.closest('div[data-highlighted-text]');
    if (commentElement) {
        const highlightedText = commentElement.dataset.highlightedText;
        highlightSelectedText(highlightedText);
    }
});

document.getElementById('comments').addEventListener('mouseout', function () {
    removeHighlight();
});

function removeHighlight() {
    const editorContent = document.getElementById('editor');
    editorContent.querySelectorAll('.highlighted').forEach(element => {
        element.outerHTML = element.innerHTML;
    });
}

function highlightSelectedText(selectedText) {
    removeHighlight();

    const editorContent = document.getElementById('editor');
    const editorText = editorContent.innerHTML;
    const highlightedText = `<span class="highlighted">${selectedText}</span>`;
    const newEditorText = editorText.replace(new RegExp(selectedText, 'g'), highlightedText);
    editorContent.innerHTML = newEditorText;
}

document.addEventListener('DOMContentLoaded', function () {
    loadComments();
});