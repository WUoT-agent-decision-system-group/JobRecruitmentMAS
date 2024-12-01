// Funkcja dodająca obiekt do pola 'applications' w dokumencie
function addApplicationToJobOffer(jobOfferId, application) {
   // Pobieranie referencji do kolekcji 'jobOffers'
   const db = connect('mongodb://localhost/aasd');
   const jobOffersCollection = db.jobOffers;

   // Aktualizacja dokumentu z danym '_id'
   const result = jobOffersCollection.updateOne(
       { _id: ObjectId(jobOfferId) },  // Szukamy dokumentu po '_id'
       { $push: { applications: application } }  // Dodajemy obiekt do tablicy 'applications'
   );

   // Sprawdzanie wyników operacji
   if (result.modifiedCount === 1) {
       print('Obiekt został dodany do tablicy applications.');
   } else {
       print('Nie znaleziono dokumentu o podanym id lub nie dokonano żadnej zmiany.');
   }
}

// Przykładowe dane
const jobOfferId = '{{JOBOFFER_ID}}';  // Podaj odpowiednie _id dokumentu
const application = {
   status: 0,
   candidateId: ObjectId('{{CANDIDATE_ID}}'),
   name: '{{CANDIDATE_NAME}}',
   surname: '{{CANDIDATE_SURNAME}}',
   email: '{{CANDIDATE_EMAIL}}',
   cv: ObjectId('{{CV_ID}}')
};

// Wywołanie funkcji
addApplicationToJobOffer(jobOfferId, application);