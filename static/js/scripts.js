// document.getElementById('toggleView').addEventListener('click', function() {
//     const table = document.getElementById('productTable');
//     const cards = document.getElementById('productCards');
    
//     if (table.style.display === 'none') {
//         table.style.display = 'table';
//         cards.style.display = 'none';
//         this.textContent = 'Switch to Card View';
//     } else {
//         table.style.display = 'none';
//         cards.style.display = 'flex';
//         this.textContent = 'Switch to Table View';
//     }
// });

// $('#exampleModal').on('show.bs.modal', function (event) {
//     var button = $(event.relatedTarget); // Button that triggered the modal
//     var id = button.data('id');
//     var name = button.data('name');
//     var age = button.data('age');
//     var grade = button.data('grade');
//     var email = button.data('email');

//     // Update the modal's content.
//     var modal = $(this);
//     modal.find('#edit-id').val(id);
//     modal.find('#edit-name').val(name);
//     modal.find('#edit-age').val(age);
//     modal.find('#edit-grade').val(grade);
//     modal.find('#edit-email').val(email);

//     // Update the form action to include the user ID
//     modal.find('#editUserForm').attr('action', '/edituser/' + id);
// });
   // Populate modal with data
   var exampleModal = document.getElementById('exampleModal');
   exampleModal.addEventListener('show.bs.modal', function (event) {
       var button = event.relatedTarget; // Button that triggered the modal
       var id = button.getAttribute('data-id');
       var fname = button.getAttribute('data-fname');
       var lname = button.getAttribute('data-lname');
       var branch = button.getAttribute('data-branch');

       // Update the modal's content.
       var modalBody = exampleModal.querySelector('.modal-body');
       modalBody.querySelector('#roll_no').value = id; // Assuming roll_no corresponds to the ID
       modalBody.querySelector('#fname').value = fname;
       modalBody.querySelector('#lname').value = lname;
       modalBody.querySelector('#branch').value = branch;

       // Update the form action to include the student ID
       var form = modalBody.querySelector('#editStudentForm');
       form.action = `/editstudent/${id}`;
   });