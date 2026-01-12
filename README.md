# SparkMate


Implemented features

1. Activity Display & Sorting
    On the homepage, the latest four activities are displayed. Activities are sorted by created_at in descending order using SQL

2. Activity Creation
    Logged-in users can create a new activity with title, description, time, location, budget, circle category, and an optional cover image.

3. Circle Hover Interaction
    On the Circles part, hovering over each circle card triggers a visual expansion revealing description text.

4. User Registration & Login
    Users may register an account and log in. 

5. Personal Profile Page
    A logged-in user can enter their account page to view their personal information, all activities they created and the number of activities they posted. Activities can be edited or deleted directly from the profile page.

6. Activity Detail Page & Like System
    Each activity has a detail page containing full information.Users can click the Like button to toggle like/unlike status without refreshing the page (AJAX request). The heart icon animates when liked, and the like count updates instantly.

7. Contact Organizer
    On the activity detail page, users may click Contact to visit the organizer’s profile page. This page only shows organizer email and organizer activities (read-only) Editing and deleting features are hidden for security and permission purposes.


Future Feature Plans

With further learning, I hope to implement the following features:
1. Near system — display activities near the user’s location
2. Advanced search — search by name, circle, and date range
3. Follow circles — users can subscribe to circles and see updates, show followed circle count on profile page
4. Join activity system — show number of participants
5. Friends system — users become friends after joining each other’s activities, show friends count on profile page
6. Allow businesses to promote their events on the platform. Sponsored events will be labeled with a “Sponsored” tag on the homepage.