"use strict";

const BASE_URL_LIKES = '/api/likes';
const BASE_URL_LIKE = '/api/like';
const BASE_URL_UNLIKE = '/api/unlike';


/** processLikeForm: handle submission of liking a cafe:
 *
 *  - makes API call to server with JSON of cafe id {"cafe_id": 1}
 *  - makes current user like cafe and receives JSON response {"liked": 1}
 */

async function processLikeForm(evt) {
  console.debug('processLikeForm ran!');
  evt.preventDefault();

  const cafe_id = $("#cafe-id").val();
  console.log('This is cafe_id', cafe_id);

  const resp = await fetch(
    BASE_URL_LIKE, {
      method: "POST",
      body: JSON.stringify({cafe_id: cafe_id}),
      headers: {
        "Content-Type": "application/json"
      }
    }
  );

  const likedData = await resp.json();
  console.log('This is likedData', likedData);

  if ("error" in likedData) {
    console.log(likedData.error);
  } else {
    $("#unlike").show();
    $("#like").hide();
  }
}

$("#like").on("click", processLikeForm);


/** processUnlikeForm: handle submission of unliking a cafe:
 *
 *  - makes API call to server with JSON of cafe id {"cafe_id": 1}
 *  - makes current user unlike cafe and receives JSON response {"unliked": 1}
 */

async function processUnlikeForm(evt) {
  console.debug('processUnlikeForm ran!');
  evt.preventDefault();

  const cafe_id = $("#cafe-id").val();
  console.log('This is cafe_id', cafe_id);

  const resp = await fetch(
    BASE_URL_UNLIKE, {
      method: "POST",
      body: JSON.stringify({cafe_id: cafe_id}),
      headers: {
        "Content-Type": "application/json"
      }
    }
  );

  const unlikedData = await resp.json();
  console.log('This is unlikedData', unlikedData);

  if ("error" in unlikedData) {
    console.log(unlikedData.error);
  } else {
    $("#unlike").hide();
    $("#like").show();
  }
}

$("#unlike").on("click", processUnlikeForm);


/** processLikes: IIFE that checks whether user currently likes specific cafe
 *
 *  Given cafe_id in the URL query string, figures out if the current user likes
 *  that cafe; receives JSON response {"likes": true|false}
 */

$(async function processLikes() {
  console.debug('processLikes ran!');

  const cafeId = $("#cafe-id").val();

  const params = new URLSearchParams({ cafe_id: cafeId });

  const resp = await fetch(`${BASE_URL_LIKES}?${params}`);

  const likesData = await resp.json();
  console.log('This is likesData=', likesData);

  if ("error" in likesData) {
    console.log(likesData.error);
  } else {
    if (likesData.likes) {
      $("#like").hide();
      $("#unlike").show();
    } else {
      $("#like").show();
      $("#unlike").hide();
    }
  }
});